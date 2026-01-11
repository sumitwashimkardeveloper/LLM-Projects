import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import pandas as pd
from pathlib import Path
from evaluator import Evaluator, EvaluationResult
from config import ModelConfig

@dataclass
class ArenaMatch:
    model_a: str
    model_b: str
    winner: str
    metrics: Dict[str, float]
    timestamp: float

class Arena:
    def __init__(self, evaluator: Evaluator):
        self.evaluator = evaluator
        self.matches: List[ArenaMatch] = []
        self.rankings: Dict[str, float] = {}

    def compare_models(self, prompt: str, reference: str = "", context: str = "") -> Dict[str, EvaluationResult]:
        model_names = list(self.evaluator.models.keys())

        results = self.evaluator.evaluate_multiple_models(model_names, prompt, reference, context)
        return results

    def run_tournament(self, prompts: List[str], references: List[str] = None, contexts: List[str] = None) -> Dict[str, Dict[str, float]]:
        references = references or [None] * len(prompts)
        contexts = contexts or [None] * len(prompts)

        model_names = list(self.evaluator.models.keys())
        model_scores = {name: {'total': 0.0, 'count': 0} for name in model_names}

        for prompt, reference, context in zip(prompts, references, contexts):
            results = self.compare_models(prompt, reference or "", context or "")

            scores = {}
            for model_name, result in results.items():
                avg_score = 0.0
                metric_count = 0

                if result.metrics:
                    for metric_name, metric_result in result.metrics.items():
                        if metric_result.score >= 0.0:
                            avg_score += metric_result.score
                            metric_count += 1

                if metric_count > 0:
                    avg_score /= metric_count

                scores[model_name] = avg_score

            max_score = max(scores.values()) if scores else 0.0

            for model_name, score in scores.items():
                if score == max_score:
                    model_scores[model_name]['total'] += 1
                model_scores[model_name]['count'] += 1

        final_rankings = {}
        for model_name, stats in model_scores.items():
            if stats['count'] > 0:
                win_rate = stats['total'] / stats['count']
                final_rankings[model_name] = win_rate
            else:
                final_rankings[model_name] = 0.0

        self.rankings = final_rankings
        return final_rankings

    def get_head_to_head(self, model_a: str, model_b: str, prompts: List[str], references: List[str] = None) -> Dict[str, any]:
        references = references or [None] * len(prompts)

        a_wins = 0
        b_wins = 0
        total_cost_a = 0.0
        total_cost_b = 0.0
        total_latency_a = 0.0
        total_latency_b = 0.0

        for prompt, reference in zip(prompts, references):
            results = self.evaluator.evaluate_multiple_models([model_a, model_b], prompt, reference or "")

            result_a = results[model_a]
            result_b = results[model_b]

            total_cost_a += result_a.response.cost
            total_cost_b += result_b.response.cost
            total_latency_a += result_a.response.latency
            total_latency_b += result_b.response.latency

            score_a = self._calculate_overall_score(result_a)
            score_b = self._calculate_overall_score(result_b)

            if score_a > score_b:
                a_wins += 1
            elif score_b > score_a:
                b_wins += 1

        return {
            'model_a': model_a,
            'model_b': model_b,
            'wins_a': a_wins,
            'wins_b': b_wins,
            'win_rate_a': a_wins / (a_wins + b_wins) if (a_wins + b_wins) > 0 else 0.0,
            'win_rate_b': b_wins / (a_wins + b_wins) if (a_wins + b_wins) > 0 else 0.0,
            'avg_cost_a': total_cost_a / len(prompts) if prompts else 0.0,
            'avg_cost_b': total_cost_b / len(prompts) if prompts else 0.0,
            'avg_latency_a': total_latency_a / len(prompts) if prompts else 0.0,
            'avg_latency_b': total_latency_b / len(prompts) if prompts else 0.0,
        }

    def _calculate_overall_score(self, result: EvaluationResult) -> float:
        if not result.metrics:
            return 0.0

        total_score = 0.0
        metric_count = 0

        for metric_result in result.metrics.values():
            total_score += metric_result.score
            metric_count += 1

        return total_score / metric_count if metric_count > 0 else 0.0

    def get_leaderboard(self, sort_by: str = 'win_rate') -> List[Tuple[str, float]]:
        leaderboard = sorted(self.rankings.items(), key=lambda x: x[1], reverse=True)
        return leaderboard

    def export_rankings_json(self, filepath: str):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.rankings, f, indent=2)

    def export_leaderboard_csv(self, filepath: str):
        leaderboard = self.get_leaderboard()
        df = pd.DataFrame(leaderboard, columns=['Model', 'Win Rate'])
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False)

    def export_arena_report(self, output_dir: str = "arena_results"):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        self.export_rankings_json(f"{output_dir}/rankings.json")
        self.export_leaderboard_csv(f"{output_dir}/leaderboard.csv")

        leaderboard = self.get_leaderboard()
        with open(f"{output_dir}/leaderboard.txt", 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("LLM ARENA LEADERBOARD\n")
            f.write("=" * 60 + "\n\n")

            for rank, (model, win_rate) in enumerate(leaderboard, 1):
                f.write(f"{rank}. {model:30s} {win_rate:.2%}\n")

            f.write("\n" + "=" * 60 + "\n")
