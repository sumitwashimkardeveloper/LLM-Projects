import torch
import time
from app.utils.metrics_utils import MetricsCollector

class ModelComparator:
    def __init__(self):
        self.models = {}

    def register_model(self, model_id, model, tokenizer):
        self.models[model_id] = {
            'model': model,
            'tokenizer': tokenizer,
            'param_count': self._count_parameters(model)
        }

    def _count_parameters(self, model):
        return sum(p.numel() for p in model.parameters())

    def _get_model_size_mb(self, model):
        param_size = sum(p.numel() * p.element_size() for p in model.parameters())
        return param_size / (1024 * 1024)

    def compare_models(self, model_ids):
        comparison = {}
        for model_id in model_ids:
            if model_id not in self.models:
                continue

            model_info = self.models[model_id]
            comparison[model_id] = {
                'param_count': model_info['param_count'],
                'size_mb': self._get_model_size_mb(model_info['model']),
                'trainable_params': self._count_trainable_parameters(model_info['model'])
            }

        return comparison

    def _count_trainable_parameters(self, model):
        return sum(p.numel() for p in model.parameters() if p.requires_grad)

    def benchmark_inference(self, model_id, input_ids, num_iterations=10):
        if model_id not in self.models:
            return None

        model = self.models[model_id]['model']
        model.eval()

        times = []
        with torch.no_grad():
            for _ in range(num_iterations):
                start = time.time()
                _ = model(input_ids)
                times.append(time.time() - start)

        return {
            'mean_latency_ms': (sum(times) / len(times)) * 1000,
            'min_latency_ms': min(times) * 1000,
            'max_latency_ms': max(times) * 1000,
            'throughput_samples_per_sec': 1 / (sum(times) / len(times))
        }

    def compare_inference_speed(self, model_ids, input_ids):
        benchmarks = {}
        for model_id in model_ids:
            result = self.benchmark_inference(model_id, input_ids)
            if result:
                benchmarks[model_id] = result

        return benchmarks


class InferenceTestor:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def test_single(self, text, max_length=100):
        inputs = self.tokenizer(text, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=max_length)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def test_batch(self, texts, max_length=100):
        results = []
        for text in texts:
            result = self.test_single(text, max_length)
            results.append(result)
        return results

    def measure_latency(self, text, num_iterations=5):
        inputs = self.tokenizer(text, return_tensors='pt')
        times = []

        with torch.no_grad():
            for _ in range(num_iterations):
                start = time.time()
                _ = self.model.generate(**inputs, max_length=50)
                times.append(time.time() - start)

        return {
            'mean_ms': (sum(times) / len(times)) * 1000,
            'std_ms': (sum((t - sum(times)/len(times))**2 for t in times) / len(times))**0.5 * 1000
        }

    def profile_memory(self, text):
        inputs = self.tokenizer(text, return_tensors='pt')
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()

        with torch.no_grad():
            _ = self.model.generate(**inputs)
            torch.cuda.synchronize()

        peak_memory = torch.cuda.max_memory_allocated() / (1024 ** 3)
        return {'peak_memory_gb': peak_memory}
