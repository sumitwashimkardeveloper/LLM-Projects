import json
import csv
from typing import List, Dict, Any
from pathlib import Path
import statistics

class DataProcessor:
    @staticmethod
    def load_json(filepath: str) -> Any:
        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_json(data: Any, filepath: str):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_csv(filepath: str) -> List[Dict[str, str]]:
        rows = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows

    @staticmethod
    def save_csv(data: List[Dict[str, Any]], filepath: str):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        if not data:
            return

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

class StatisticsCalculator:
    @staticmethod
    def calculate_mean(values: List[float]) -> float:
        return statistics.mean(values) if values else 0.0

    @staticmethod
    def calculate_median(values: List[float]) -> float:
        return statistics.median(values) if values else 0.0

    @staticmethod
    def calculate_stdev(values: List[float]) -> float:
        return statistics.stdev(values) if len(values) > 1 else 0.0

    @staticmethod
    def calculate_min_max(values: List[float]) -> tuple:
        if not values:
            return (0.0, 0.0)
        return (min(values), max(values))

    @staticmethod
    def calculate_percentile(values: List[float], percentile: float) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

class ReportGenerator:
    @staticmethod
    def generate_text_report(data: Dict[str, Any], filepath: str):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("LLM EVALUATION REPORT\n")
            f.write("=" * 80 + "\n\n")

            for section, content in data.items():
                f.write(f"\n{section.upper()}\n")
                f.write("-" * 80 + "\n")

                if isinstance(content, dict):
                    for key, value in content.items():
                        if isinstance(value, float):
                            f.write(f"{key}: {value:.4f}\n")
                        else:
                            f.write(f"{key}: {value}\n")
                elif isinstance(content, list):
                    for item in content:
                        f.write(f"  {item}\n")
                else:
                    f.write(f"{content}\n")

                f.write("\n")

            f.write("=" * 80 + "\n")

    @staticmethod
    def generate_html_report(data: Dict[str, Any], filepath: str):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>LLM Evaluation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #007bff; color: white; }
        tr:hover { background: #f9f9f9; }
        .metric { display: inline-block; background: #e7f3ff; padding: 10px 15px; margin: 5px; border-radius: 5px; }
        .score { font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>LLM Evaluation Report</h1>
"""

        for section, content in data.items():
            html_content += f"<h2>{section.title()}</h2>\n"

            if isinstance(content, dict):
                html_content += "<table>\n<tr><th>Metric</th><th>Value</th></tr>\n"
                for key, value in content.items():
                    if isinstance(value, float):
                        html_content += f"<tr><td>{key}</td><td><span class='score'>{value:.4f}</span></td></tr>\n"
                    else:
                        html_content += f"<tr><td>{key}</td><td>{value}</td></tr>\n"
                html_content += "</table>\n"

            elif isinstance(content, list):
                for item in content:
                    html_content += f"<p class='metric'>{item}</p>\n"

        html_content += """
    </div>
</body>
</html>
"""

        with open(filepath, 'w') as f:
            f.write(html_content)

class ComparisonAnalyzer:
    @staticmethod
    def compare_metrics(results: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        analysis = {}

        for model_name, values in results.items():
            analysis[model_name] = {
                'mean': StatisticsCalculator.calculate_mean(values),
                'median': StatisticsCalculator.calculate_median(values),
                'stdev': StatisticsCalculator.calculate_stdev(values),
                'min': StatisticsCalculator.calculate_min_max(values)[0],
                'max': StatisticsCalculator.calculate_min_max(values)[1],
                'p95': StatisticsCalculator.calculate_percentile(values, 95)
            }

        return analysis

    @staticmethod
    def rank_models(metrics: Dict[str, float]) -> List[tuple]:
        return sorted(metrics.items(), key=lambda x: x[1], reverse=True)

    @staticmethod
    def calculate_efficiency_score(cost: float, latency: float, quality: float) -> float:
        if cost == 0 or latency == 0:
            return quality * 100

        efficiency = (quality * 100) / (cost + latency)
        return efficiency

class PromptTemplateEngine:
    @staticmethod
    def create_evaluation_prompt(task: str, context: str = "") -> str:
        prompt = f"Task: {task}"
        if context:
            prompt += f"\nContext: {context}"
        prompt += "\n\nProvide a detailed and accurate response."
        return prompt

    @staticmethod
    def create_comparison_prompt(models: List[str], question: str) -> str:
        prompt = f"Compare the following models: {', '.join(models)}\n"
        prompt += f"Question: {question}\n"
        prompt += "Rate each model's response quality."
        return prompt

class ResultsCache:
    def __init__(self, cache_file: str = "cache/eval_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        if Path(self.cache_file).exists():
            return DataProcessor.load_json(self.cache_file)
        return {}

    def get(self, key: str) -> Any:
        return self.cache.get(key)

    def set(self, key: str, value: Any):
        self.cache[key] = value
        self._save_cache()

    def _save_cache(self):
        DataProcessor.save_json(self.cache, self.cache_file)

    def clear(self):
        self.cache = {}
        self._save_cache()

    def has_key(self, key: str) -> bool:
        return key in self.cache
