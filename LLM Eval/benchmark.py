import time
from typing import List, Dict, Tuple
from dataclasses import dataclass
from evaluator import Evaluator, EvaluationResult
from config import ModelConfig
import json
from pathlib import Path

@dataclass
class BenchmarkResult:
    name: str
    model_name: str
    total_time: float
    results_count: int
    avg_latency: float
    total_cost: float
    avg_quality_score: float

class Benchmark:
    def __init__(self, evaluator: Evaluator):
        self.evaluator = evaluator
        self.benchmark_results = []

    def run_latency_benchmark(self, model_name: str, prompts: List[str], iterations: int = 1) -> BenchmarkResult:
        total_latency = 0.0
        results_count = 0

        start_time = time.time()

        for _ in range(iterations):
            for prompt in prompts:
                try:
                    result = self.evaluator.evaluate_single(model_name, prompt)
                    total_latency += result.response.latency
                    results_count += 1
                except Exception as e:
                    print(f"Error: {e}")

        total_time = time.time() - start_time
        avg_latency = total_latency / results_count if results_count > 0 else 0.0

        benchmark = BenchmarkResult(
            name="Latency",
            model_name=model_name,
            total_time=total_time,
            results_count=results_count,
            avg_latency=avg_latency,
            total_cost=0.0,
            avg_quality_score=0.0
        )

        self.benchmark_results.append(benchmark)
        return benchmark

    def run_cost_benchmark(self, model_name: str, prompts: List[str]) -> BenchmarkResult:
        total_cost = 0.0
        results_count = 0

        start_time = time.time()

        for prompt in prompts:
            try:
                result = self.evaluator.evaluate_single(model_name, prompt)
                total_cost += result.response.cost
                results_count += 1
            except Exception as e:
                print(f"Error: {e}")

        total_time = time.time() - start_time

        benchmark = BenchmarkResult(
            name="Cost",
            model_name=model_name,
            total_time=total_time,
            results_count=results_count,
            avg_latency=0.0,
            total_cost=total_cost,
            avg_quality_score=0.0
        )

        self.benchmark_results.append(benchmark)
        return benchmark

    def run_quality_benchmark(self, model_name: str, prompts: List[str], references: List[str]) -> BenchmarkResult:
        total_quality = 0.0
        results_count = 0

        start_time = time.time()

        for prompt, reference in zip(prompts, references):
            try:
                result = self.evaluator.evaluate_single(model_name, prompt, reference)

                if result.metrics:
                    metric_scores = [m.score for m in result.metrics.values()]
                    avg_score = sum(metric_scores) / len(metric_scores) if metric_scores else 0.0
                    total_quality += avg_score
                    results_count += 1
            except Exception as e:
                print(f"Error: {e}")

        total_time = time.time() - start_time
        avg_quality = total_quality / results_count if results_count > 0 else 0.0

        benchmark = BenchmarkResult(
            name="Quality",
            model_name=model_name,
            total_time=total_time,
            results_count=results_count,
            avg_latency=0.0,
            total_cost=0.0,
            avg_quality_score=avg_quality
        )

        self.benchmark_results.append(benchmark)
        return benchmark

    def run_throughput_benchmark(self, model_name: str, prompts: List[str], duration_seconds: int = 10) -> BenchmarkResult:
        results_count = 0
        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            for prompt in prompts:
                try:
                    self.evaluator.evaluate_single(model_name, prompt)
                    results_count += 1
                except Exception as e:
                    print(f"Error: {e}")

                if time.time() - start_time >= duration_seconds:
                    break

        total_time = time.time() - start_time
        throughput = results_count / total_time if total_time > 0 else 0.0

        benchmark = BenchmarkResult(
            name="Throughput",
            model_name=model_name,
            total_time=total_time,
            results_count=results_count,
            avg_latency=0.0,
            total_cost=0.0,
            avg_quality_score=throughput
        )

        self.benchmark_results.append(benchmark)
        return benchmark

    def run_comprehensive_benchmark(self, model_name: str, prompts: List[str], references: List[str] = None) -> Dict[str, BenchmarkResult]:
        print(f"\nRunning comprehensive benchmark for {model_name}...")

        results = {}

        print("  Running latency benchmark...")
        results['latency'] = self.run_latency_benchmark(model_name, prompts[:5], iterations=1)

        print("  Running cost benchmark...")
        results['cost'] = self.run_cost_benchmark(model_name, prompts[:5])

        if references:
            print("  Running quality benchmark...")
            results['quality'] = self.run_quality_benchmark(model_name, prompts[:5], references[:5])

        print("  Running throughput benchmark...")
        results['throughput'] = self.run_throughput_benchmark(model_name, prompts[:3], duration_seconds=5)

        return results

    def compare_benchmarks(self, model_names: List[str], benchmark_name: str) -> Dict[str, BenchmarkResult]:
        comparison = {}

        for result in self.benchmark_results:
            if result.name == benchmark_name:
                if result.model_name not in comparison or result.total_time < comparison[result.model_name].total_time:
                    comparison[result.model_name] = result

        return comparison

    def get_fastest_model(self, prompts: List[str]) -> Tuple[str, float]:
        latencies = {}

        for result in self.benchmark_results:
            if result.name == "Latency":
                latencies[result.model_name] = result.avg_latency

        if not latencies:
            return None, float('inf')

        fastest = min(latencies.items(), key=lambda x: x[1])
        return fastest

    def get_cheapest_model(self, prompts: List[str]) -> Tuple[str, float]:
        costs = {}

        for result in self.benchmark_results:
            if result.name == "Cost":
                costs[result.model_name] = result.total_cost

        if not costs:
            return None, float('inf')

        cheapest = min(costs.items(), key=lambda x: x[1])
        return cheapest

    def get_best_quality_model(self, prompts: List[str]) -> Tuple[str, float]:
        qualities = {}

        for result in self.benchmark_results:
            if result.name == "Quality":
                qualities[result.model_name] = result.avg_quality_score

        if not qualities:
            return None, 0.0

        best = max(qualities.items(), key=lambda x: x[1])
        return best

    def get_highest_throughput_model(self, prompts: List[str]) -> Tuple[str, float]:
        throughputs = {}

        for result in self.benchmark_results:
            if result.name == "Throughput":
                throughputs[result.model_name] = result.avg_quality_score

        if not throughputs:
            return None, 0.0

        best = max(throughputs.items(), key=lambda x: x[1])
        return best

    def export_benchmark_report(self, output_dir: str = "benchmark_results"):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        results_data = []
        for result in self.benchmark_results:
            results_data.append({
                'benchmark': result.name,
                'model': result.model_name,
                'total_time': result.total_time,
                'results_count': result.results_count,
                'avg_latency': result.avg_latency,
                'total_cost': result.total_cost,
                'avg_quality_score': result.avg_quality_score
            })

        with open(f"{output_dir}/benchmark_results.json", 'w') as f:
            json.dump(results_data, f, indent=2)

        with open(f"{output_dir}/benchmark_summary.txt", 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("BENCHMARK SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            latency_result = self.get_fastest_model([])
            cost_result = self.get_cheapest_model([])
            quality_result = self.get_best_quality_model([])
            throughput_result = self.get_highest_throughput_model([])

            f.write("FASTEST MODEL:\n")
            if latency_result[0]:
                f.write(f"  {latency_result[0]}: {latency_result[1]:.4f}s average latency\n\n")

            f.write("CHEAPEST MODEL:\n")
            if cost_result[0]:
                f.write(f"  {cost_result[0]}: ${cost_result[1]:.6f} total cost\n\n")

            f.write("BEST QUALITY MODEL:\n")
            if quality_result[0]:
                f.write(f"  {quality_result[0]}: {quality_result[1]:.4f} average quality score\n\n")

            f.write("HIGHEST THROUGHPUT MODEL:\n")
            if throughput_result[0]:
                f.write(f"  {throughput_result[0]}: {throughput_result[1]:.2f} requests/second\n\n")

            f.write("\nDETAILED RESULTS:\n")
            f.write("-" * 80 + "\n\n")

            for result in self.benchmark_results:
                f.write(f"Benchmark: {result.name} | Model: {result.model_name}\n")
                f.write(f"  Total Time: {result.total_time:.2f}s\n")
                f.write(f"  Results Count: {result.results_count}\n")
                if result.avg_latency > 0:
                    f.write(f"  Avg Latency: {result.avg_latency:.4f}s\n")
                if result.total_cost > 0:
                    f.write(f"  Total Cost: ${result.total_cost:.6f}\n")
                if result.avg_quality_score > 0:
                    f.write(f"  Quality Score: {result.avg_quality_score:.4f}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
