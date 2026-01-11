from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum

class ModelProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LLAMA = "llama"

class MetricType(Enum):
    BLEU = "bleu"
    ROUGE = "rouge"
    BERTSCORE = "bertscore"
    HALLUCINATION = "hallucination"
    FAITHFULNESS = "faithfulness"
    TOXICITY = "toxicity"
    LATENCY = "latency"
    COST = "cost"

@dataclass
class ModelConfig:
    provider: ModelProvider
    model_name: str
    api_key: str = ""
    base_url: str = ""
    max_tokens: int = 2048
    temperature: float = 0.7

@dataclass
class EvalConfig:
    batch_size: int = 32
    num_workers: int = 4
    timeout: int = 60
    cache_responses: bool = True
    metrics: list = field(default_factory=lambda: [
        MetricType.BLEU,
        MetricType.ROUGE,
        MetricType.BERTSCORE,
        MetricType.HALLUCINATION,
        MetricType.FAITHFULNESS,
        MetricType.TOXICITY,
        MetricType.LATENCY,
        MetricType.COST
    ])

OPENAI_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}

CLAUDE_PRICING = {
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
}

GEMINI_PRICING = {
    "gemini-pro": {"input": 0.0, "output": 0.0},
    "gemini-pro-vision": {"input": 0.0, "output": 0.0},
}

LLAMA_PRICING = {
    "llama-2-7b": {"input": 0.0, "output": 0.0},
    "llama-2-13b": {"input": 0.0, "output": 0.0},
    "llama-2-70b": {"input": 0.0, "output": 0.0},
}
