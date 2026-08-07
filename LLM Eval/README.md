# LLM Evaluation Framework

A **comprehensive, production-grade framework** for evaluating and benchmarking large language models (LLMs) across multiple dimensions including accuracy, latency, cost, and quality metrics. Compare models systematically, run tournaments, and make data-driven decisions about model selection.

## 🎯 Overview

Evaluating LLMs is complex. This framework provides:
- **Multi-metric evaluation** — BLEU, ROUGE, BERTScore, hallucination detection, toxicity
- **Cost tracking** — Measure per-token costs across different providers
- **Performance benchmarking** — Latency, throughput, and quality analysis
- **Model comparison** — Head-to-head and tournament-style rankings
- **Statistical analysis** — Comprehensive reporting and export capabilities

**Supported Providers:**
- Anthropic Claude (claude-3-opus, claude-3-sonnet, claude-3-haiku)
- OpenAI GPT (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
- Google Gemini (gemini-pro, gemini-pro-vision)
- Local Llama (llama-2-7b, llama-2-13b, llama-2-70b)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- API keys for providers you want to evaluate
- 2GB+ RAM for local model support

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Edit .env with your API keys
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=...
```

### Basic Usage

```python
from config import ModelConfig, ModelProvider
from evaluator import Evaluator

# Create evaluator
evaluator = Evaluator()

# Register models
claude_config = ModelConfig(
    provider=ModelProvider.CLAUDE,
    model_name="claude-3-haiku-20240307"
)
evaluator.register_model("Claude-3-Haiku", claude_config)

# Evaluate a prompt
result = evaluator.evaluate_single(
    model_name="Claude-3-Haiku",
    prompt="What is machine learning?",
    reference="Machine learning is a subset of AI..."
)

print(f"Latency: {result.latency:.2f}s")
print(f"Cost: ${result.cost:.4f}")
print(f"Quality Metrics: {result.metrics}")
```

### Run Examples

```bash
# Quick start with all features
python quick_start.py

# Comprehensive examples
python examples.py

# Run tests
python test_framework.py

# Interactive CLI
python main.py
```

## 📊 Evaluation Metrics

### Accuracy Metrics (Text Similarity)

**BLEU Score** (0-1)
- Measures n-gram overlap between generated and reference text
- Commonly used in machine translation
- Higher is better; 1.0 is perfect match
- Quick to compute but ignores semantics

**ROUGE Score** (0-1)
- Recall-Oriented Understudy for Gisting Evaluation
- Measures recall of n-grams, longest common subsequence, skip-bigrams
- Better for summarization evaluation
- Multiple variants: ROUGE-1, ROUGE-2, ROUGE-L
- Higher is better

**BERTScore** (0-1)
- Uses contextual embeddings from BERT for semantic similarity
- Captures semantic meaning beyond surface-level n-grams
- More robust to paraphrasing
- Higher is better; most reliable accuracy metric

### Quality Metrics

**Hallucination Detection** (0-1)
- Detects factually incorrect or made-up information
- Score 0-1 where 1.0 = no hallucinations
- Uses semantic matching and fact verification
- Critical for factual tasks

**Faithfulness** (0-1)
- Measures how well output adheres to source/context
- Score 0-1 where 1.0 = perfectly faithful
- Evaluates consistency with provided information
- Important for instruction-following

**Toxicity Detection** (0-1)
- Detects harmful, offensive, or unsafe language
- Score 0-1 where 1.0 = no toxic content
- Ensures model outputs are safe
- Important for production deployments

### Performance Metrics

**Latency** (seconds)
- End-to-end response time
- Includes: API overhead, network, inference, post-processing
- Lower is better; affects user experience
- Measure under consistent conditions

**Cost** (USD)
- Per-token pricing based on provider rates
- Tracks input and output tokens separately
- Multiply by usage volume for total cost
- Essential for budgeting

**Throughput** (requests/second)
- How many requests a model can handle per second
- Higher is better; indicates capacity
- Important for production scaling

## 🏆 Arena & Benchmarking

### Arena Tournament Mode
Run a tournament where all models answer the same prompts:

```python
from arena import Arena

arena = Arena(evaluator)

# Run tournament
rankings = arena.run_tournament(
    prompts=["What is AI?", "Explain machine learning"],
    references=["AI is...", "ML is..."],
    models=["Claude", "GPT-4", "Gemini"]
)

# View rankings (win rates)
for model, win_rate in rankings.items():
    print(f"{model}: {win_rate:.1%}")

# Export results
arena.export_arena_report("tournament_results")
```

### Head-to-Head Comparison
Compare two specific models:

```python
result = arena.get_head_to_head(
    model_1="Claude-3-Opus",
    model_2="GPT-4",
    prompts=[...],
    references=[...]
)

print(f"Claude wins: {result['Claude-3-Opus']:.1%}")
print(f"GPT-4 wins: {result['GPT-4']:.1%}")
```

### Benchmarking Suite

**Latency Benchmark**
```python
from benchmark import Benchmark

benchmark = Benchmark(evaluator)
result = benchmark.run_latency_benchmark(
    model_name="Claude",
    prompts=prompts,
    iterations=10
)
print(f"Average latency: {result['average']:.2f}s")
print(f"P95 latency: {result['p95']:.2f}s")
```

**Cost Benchmark**
```python
result = benchmark.run_cost_benchmark(
    models=["Claude", "GPT-4", "Gemini"],
    prompts=prompts
)
# Compare total cost and cost per token
```

**Quality Benchmark**
```python
result = benchmark.run_quality_benchmark(
    models=["Claude", "GPT-4"],
    prompts=prompts,
    references=references
)
# Get aggregate quality scores
```

**Throughput Benchmark**
```python
result = benchmark.run_throughput_benchmark(
    model_name="Claude",
    duration_seconds=60
)
print(f"Throughput: {result['requests_per_second']:.2f} req/s")
```

## 📁 Project Structure

```
LLM Eval/
├── config.py                 # Configuration and constants
│   ├── ModelConfig          # Provider/model configuration
│   ├── ModelProvider        # Enum: CLAUDE, OPENAI, GEMINI, LLAMA
│   ├── MetricType          # Enum: BLEU, ROUGE, BERTSCORE, etc.
│   └── PRICING             # Provider pricing data
│
├── metrics.py              # Evaluation metrics
│   ├── BLEUMetric         # N-gram overlap
│   ├── ROUGEMetric        # Recall-based scoring
│   ├── BERTScoreMetric    # Semantic similarity
│   ├── HallucinationDetector
│   ├── FaithfulnessDetector
│   ├── ToxicityDetector
│   └── MetricsEngine      # Orchestrates all metrics
│
├── models.py              # LLM provider integrations
│   ├── BaseModel          # Abstract base class
│   ├── OpenAIModel        # GPT implementation
│   ├── ClaudeModel        # Claude implementation
│   ├── GeminiModel        # Gemini implementation
│   ├── LlamaModel         # Llama implementation
│   └── ModelFactory       # Factory pattern
│
├── evaluator.py           # Core evaluation engine
│   ├── Evaluator          # Main class
│   ├── evaluate_single()  # Single prompt evaluation
│   ├── evaluate_batch()   # Multiple prompts
│   └── generate_report()  # Export results
│
├── arena.py              # Model comparison
│   ├── Arena             # Tournament management
│   ├── run_tournament()  # Multi-model tournament
│   ├── get_head_to_head()
│   └── export_arena_report()
│
├── benchmark.py          # Performance benchmarking
│   ├── Benchmark
│   ├── run_latency_benchmark()
│   ├── run_cost_benchmark()
│   ├── run_quality_benchmark()
│   └── run_throughput_benchmark()
│
├── utils.py             # Utilities
│   ├── DataProcessor    # JSON/CSV handling
│   ├── StatisticsCalculator
│   ├── ReportGenerator  # Report creation
│   ├── ComparisonAnalyzer
│   ├── PromptTemplateEngine
│   └── ResultsCache     # Response caching
│
├── main.py              # Interactive CLI
├── quick_start.py       # Quick start guide
├── examples.py          # Usage examples
├── test_framework.py    # Unit tests
├── requirements.txt
├── .env.example
├── plan.md             # Development roadmap
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

```env
# API Keys (add keys for providers you want to use)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Optional: Local Llama model path
LLAMA_MODEL_PATH=/models/llama-2-7b-q4.gguf

# Evaluation Settings
BATCH_SIZE=4
NUM_WORKERS=2
CACHE_RESPONSES=true

# Request timeout
REQUEST_TIMEOUT_S=120

# Rate limiting (requests per minute)
RATE_LIMIT_RPM=60
```

### Model Configuration

Register models in code:

```python
from config import ModelConfig, ModelProvider

configs = {
    "claude-opus": ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_name="claude-3-opus-20240229"
    ),
    "gpt-4": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4"
    ),
    "gemini-pro": ModelConfig(
        provider=ModelProvider.GEMINI,
        model_name="gemini-pro"
    ),
}

for name, config in configs.items():
    evaluator.register_model(name, config)
```

## 🧪 Testing

```bash
# Run all tests
python test_framework.py

# Run specific test
python -m pytest test_framework.py::TestMetrics -v

# With coverage
python -m pytest test_framework.py --cov=. --cov-report=html
```

**Tests cover:**
- All metric implementations
- Evaluator functionality
- Model integration
- Configuration validation
- Data processors
- Statistical calculations

## 📈 Output & Results

### Evaluation Results
```json
{
  "model": "Claude-3-Opus",
  "prompt": "What is AI?",
  "response": "Artificial Intelligence is...",
  "latency": 0.234,
  "cost": 0.000234,
  "tokens": {
    "input": 12,
    "output": 45,
    "total": 57
  },
  "metrics": {
    "bleu": 0.8234,
    "rouge": 0.7654,
    "bertscore": 0.8923,
    "hallucination": 0.95,
    "faithfulness": 0.92,
    "toxicity": 0.99
  }
}
```

### Arena Rankings
```json
{
  "Claude-3-Opus": 0.67,
  "GPT-4": 0.56,
  "Claude-3-Sonnet": 0.45,
  "Gemini-Pro": 0.32
}
```

### Benchmark Results
```json
{
  "model": "Claude-3-Opus",
  "latency": {
    "mean": 0.234,
    "p50": 0.210,
    "p95": 0.450,
    "p99": 0.890
  },
  "cost": {
    "total": 12.34,
    "per_token": 0.000234,
    "input_tokens": 500,
    "output_tokens": 1200
  }
}
```

## 🔐 Security Considerations

- ✅ API keys stored in `.env` (never commit!)
- ✅ No logging of sensitive prompt/response content
- ✅ Local evaluation for sensitive data (use Llama)
- ✅ Rate limiting to avoid API abuse
- ✅ Caching to minimize API calls

## 🐛 Troubleshooting

### Import Errors
```bash
# Download required NLTK data
python -c "import nltk; nltk.download('punkt')"

# Install all dependencies
pip install -r requirements.txt --upgrade
```

### API Key Issues
- Verify keys in `.env` file
- Test key validity: `python -c "from models import *; ..."`
- Check provider rate limits
- Ensure sufficient API credits

### Memory Issues
- Reduce `BATCH_SIZE`
- Process prompts in smaller batches
- Use local Llama instead of cloud APIs
- Enable `CACHE_RESPONSES` for reusable evaluations

### Model Not Found
- Verify `model_name` matches provider's model ID exactly
- Check provider documentation for available models
- Ensure API key has access to the model

## 📚 Examples

See `examples.py` for complete working examples of:
- Single model evaluation
- Multi-model comparison
- Batch evaluation
- Arena tournaments
- Head-to-head comparison
- Hallucination detection
- Cost comparison
- Latency analysis

## 🎓 Learn More

- [USAGE.txt](./USAGE.txt) — Detailed usage guide
- [PROJECT_OVERVIEW.txt](./PROJECT_OVERVIEW.txt) — Comprehensive overview
- [plan.md](./plan.md) — Development roadmap
- OpenAI API docs: https://platform.openai.com/docs
- Anthropic API docs: https://docs.anthropic.com
- HuggingFace Transformers: https://huggingface.co/transformers/

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 💬 Support

- **GitHub Issues** — Report bugs and request features
- **Discussions** — Ask questions and share ideas
- **Email** — support@llm-eval.com

---

**Built for evaluating, comparing, and selecting the best LLMs for your use case.**
