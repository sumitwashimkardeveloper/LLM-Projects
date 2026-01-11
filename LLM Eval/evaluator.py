import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from config import ModelConfig, EvalConfig, MetricType, ModelProvider
from models import ModelFactory, ModelResponse
from metrics import MetricsEngine, MetricResult
import pandas as pd
from pathlib import Path

@dataclass
class EvaluationResult:
    model_name: str
    prompt: str
    reference: str
    response: ModelResponse
    metrics: Dict[str, MetricResult]
    timestamp: float

class Evaluator:
    def __init__(self, eval_config: EvalConfig = None):
        self.eval_config = eval_config or EvalConfig()
        self.metrics_engine = MetricsEngine()
        self.results = []
        self.models: Dict[str, Any] = {}

    def register_model(self, name: str, config: ModelConfig):
        self.models[name] = ModelFactory.create_model(config)

    def evaluate_single(self, model_name: str, prompt: str, reference: str = "", context: str = "") -> EvaluationResult:
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not registered")

        model = self.models[model_name]

        start_time = time.time()
        response = model.generate(prompt)
        generation_time = time.time() - start_time

        if reference:
            metrics = self.metrics_engine.compute_all(reference, response.text, context)
        else:
            metrics = {}

        result = EvaluationResult(
            model_name=model_name,
            prompt=prompt,
            reference=reference,
            response=response,
            metrics=metrics,
            timestamp=start_time
        )

        self.results.append(result)
        return result

    def evaluate_batch(self, model_name: str, prompts: List[str], references: List[str] = None, contexts: List[str] = None) -> List[EvaluationResult]:
        results = []
        references = references or [None] * len(prompts)
        contexts = contexts or [None] * len(prompts)

        for i, (prompt, reference, context) in enumerate(zip(prompts, references, contexts)):
            result = self.evaluate_single(model_name, prompt, reference or "", context or "")
            results.append(result)

        return results

    def evaluate_multiple_models(self, model_names: List[str], prompt: str, reference: str = "", context: str = "") -> Dict[str, EvaluationResult]:
        results = {}

        for model_name in model_names:
            result = self.evaluate_single(model_name, prompt, reference, context)
            results[model_name] = result

        return results

    def get_summary_stats(self) -> Dict[str, Dict[str, float]]:
        if not self.results:
            return {}

        summary = {}

        for result in self.results:
            if result.model_name not in summary:
                summary[result.model_name] = {
                    'avg_latency': 0.0,
                    'total_cost': 0.0,
                    'avg_bleu': 0.0,
                    'avg_rouge': 0.0,
                    'avg_bertscore': 0.0,
                    'avg_hallucination': 0.0,
                    'avg_faithfulness': 0.0,
                    'avg_toxicity': 0.0,
                    'count': 0
                }

            stats = summary[result.model_name]
            stats['avg_latency'] += result.response.latency
            stats['total_cost'] += result.response.cost

            if result.metrics:
                stats['avg_bleu'] += result.metrics.get('bleu', MetricResult('bleu', 0.0)).score
                stats['avg_rouge'] += result.metrics.get('rouge', MetricResult('rouge', 0.0)).score
                stats['avg_bertscore'] += result.metrics.get('bertscore', MetricResult('bertscore', 0.0)).score
                stats['avg_hallucination'] += result.metrics.get('hallucination', MetricResult('hallucination', 0.0)).score
                stats['avg_faithfulness'] += result.metrics.get('faithfulness', MetricResult('faithfulness', 0.0)).score
                stats['avg_toxicity'] += result.metrics.get('toxicity', MetricResult('toxicity', 0.0)).score

            stats['count'] += 1

        for model_name in summary:
            count = summary[model_name]['count']
            if count > 0:
                summary[model_name]['avg_latency'] /= count
                summary[model_name]['avg_bleu'] /= count
                summary[model_name]['avg_rouge'] /= count
                summary[model_name]['avg_bertscore'] /= count
                summary[model_name]['avg_hallucination'] /= count
                summary[model_name]['avg_faithfulness'] /= count
                summary[model_name]['avg_toxicity'] /= count

        return summary

    def export_results_json(self, filepath: str):
        results_data = []

        for result in self.results:
            result_dict = {
                'model_name': result.model_name,
                'prompt': result.prompt,
                'reference': result.reference,
                'response': result.response.text,
                'latency': result.response.latency,
                'input_tokens': result.response.input_tokens,
                'output_tokens': result.response.output_tokens,
                'cost': result.response.cost,
                'timestamp': result.timestamp,
                'metrics': {}
            }

            for metric_name, metric_result in result.metrics.items():
                result_dict['metrics'][metric_name] = {
                    'score': metric_result.score,
                    'details': metric_result.details
                }

            results_data.append(result_dict)

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)

    def export_results_csv(self, filepath: str):
        if not self.results:
            return

        data = []

        for result in self.results:
            row = {
                'model': result.model_name,
                'latency': result.response.latency,
                'cost': result.response.cost,
                'input_tokens': result.response.input_tokens,
                'output_tokens': result.response.output_tokens,
            }

            for metric_name, metric_result in result.metrics.items():
                row[f'{metric_name}_score'] = metric_result.score

            data.append(row)

        df = pd.DataFrame(data)
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False)

    def generate_report(self, output_dir: str = "eval_results"):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        self.export_results_json(f"{output_dir}/results.json")
        self.export_results_csv(f"{output_dir}/results.csv")

        summary = self.get_summary_stats()
        with open(f"{output_dir}/summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
