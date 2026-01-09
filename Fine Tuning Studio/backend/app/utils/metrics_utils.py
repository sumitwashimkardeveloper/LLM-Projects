import json
import os
from datetime import datetime

class MetricsCollector:
    def __init__(self, job_id, output_dir):
        self.job_id = job_id
        self.output_dir = output_dir
        self.metrics_file = os.path.join(output_dir, 'metrics.jsonl')
        os.makedirs(output_dir, exist_ok=True)

    def log_metric(self, step, loss, eval_loss=None, accuracy=None, learning_rate=None):
        metric = {
            'step': step,
            'timestamp': datetime.utcnow().isoformat(),
            'loss': loss,
            'eval_loss': eval_loss,
            'accuracy': accuracy,
            'learning_rate': learning_rate
        }
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')

    def get_metrics_summary(self):
        if not os.path.exists(self.metrics_file):
            return None

        metrics = []
        with open(self.metrics_file, 'r') as f:
            for line in f:
                if line.strip():
                    metrics.append(json.loads(line))

        if not metrics:
            return None

        return {
            'total_steps': len(metrics),
            'min_loss': min(m['loss'] for m in metrics),
            'max_loss': max(m['loss'] for m in metrics),
            'final_loss': metrics[-1]['loss'],
            'avg_loss': sum(m['loss'] for m in metrics) / len(metrics),
            'metrics': metrics
        }

    def get_latest_metrics(self, limit=100):
        if not os.path.exists(self.metrics_file):
            return []

        metrics = []
        with open(self.metrics_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                if line.strip():
                    metrics.append(json.loads(line))

        return metrics


class ResourceMonitor:
    def __init__(self):
        self.samples = []

    def log_resource(self, step, gpu_memory_mb=None, cpu_percent=None, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()

        resource = {
            'step': step,
            'timestamp': timestamp,
            'gpu_memory_mb': gpu_memory_mb,
            'cpu_percent': cpu_percent
        }
        self.samples.append(resource)

    def get_resource_summary(self):
        if not self.samples:
            return None

        gpu_samples = [s['gpu_memory_mb'] for s in self.samples if s['gpu_memory_mb'] is not None]
        cpu_samples = [s['cpu_percent'] for s in self.samples if s['cpu_percent'] is not None]

        return {
            'gpu_memory_mb': {
                'min': min(gpu_samples) if gpu_samples else None,
                'max': max(gpu_samples) if gpu_samples else None,
                'avg': sum(gpu_samples) / len(gpu_samples) if gpu_samples else None
            },
            'cpu_percent': {
                'min': min(cpu_samples) if cpu_samples else None,
                'max': max(cpu_samples) if cpu_samples else None,
                'avg': sum(cpu_samples) / len(cpu_samples) if cpu_samples else None
            }
        }
