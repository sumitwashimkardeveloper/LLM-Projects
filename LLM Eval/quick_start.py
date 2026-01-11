import os
from dotenv import load_dotenv
from config import ModelConfig, ModelProvider, EvalConfig
from evaluator import Evaluator
from arena import Arena
from benchmark import Benchmark

load_dotenv()

def quick_start():
    print("\n" + "=" * 70)
    print("LLM EVALUATION FRAMEWORK - QUICK START")
    print("=" * 70)

    eval_config = EvalConfig()
    evaluator = Evaluator(eval_config)

    print("\n[1/4] Registering models...")

    claude_config = ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_name="claude-3-haiku-20240307",
        api_key=os.getenv("ANTHROPIC_API_KEY", "")
    )

    openai_config = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY", "")
    )

    gemini_config = ModelConfig(
        provider=ModelProvider.GEMINI,
        model_name="gemini-pro",
        api_key=os.getenv("GEMINI_API_KEY", "")
    )

    models_to_register = [
        ("Claude", claude_config),
        ("GPT-3.5", openai_config),
        ("Gemini", gemini_config)
    ]

    for model_name, config in models_to_register:
        try:
            evaluator.register_model(model_name, config)
            print(f"  ✓ {model_name}")
        except Exception as e:
            print(f"  ✗ {model_name}: API key missing or invalid")

    if not evaluator.models:
        print("\n✗ Error: No models registered. Please set API keys in .env file")
        print("  Copy .env.example to .env and fill in your API keys")
        return

    print(f"\n[2/4] Single evaluation with {list(evaluator.models.keys())[0]}...")

    prompt = "What is the Python programming language?"
    reference = "Python is a high-level, interpreted programming language known for its simplicity and readability."

    try:
        result = evaluator.evaluate_single(list(evaluator.models.keys())[0], prompt, reference)

        print(f"  Prompt: {prompt}")
        print(f"  Response: {result.response.text[:80]}...")
        print(f"  Latency: {result.response.latency:.3f}s")
        print(f"  Cost: ${result.response.cost:.6f}")

        if result.metrics:
            print("  Metrics:")
            for metric_name, metric in result.metrics.items():
                print(f"    - {metric_name}: {metric.score:.4f}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print(f"\n[3/4] Running arena tournament...")

    if len(evaluator.models) >= 2:
        arena = Arena(evaluator)

        tournament_prompts = [
            "Explain machine learning",
            "What is artificial intelligence?",
            "Describe deep learning"
        ]

        tournament_refs = [
            "Machine learning enables systems to learn from data.",
            "AI simulates human intelligence through computer systems.",
            "Deep learning uses multiple neural network layers."
        ]

        try:
            rankings = arena.run_tournament(tournament_prompts, tournament_refs)

            print("  Tournament Results:")
            for model, win_rate in sorted(rankings.items(), key=lambda x: x[1], reverse=True):
                print(f"    {model}: {win_rate:.1%} win rate")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    else:
        print("  Skipped: Need at least 2 models")

    print(f"\n[4/4] Running benchmark...")

    try:
        benchmark = Benchmark(evaluator)

        benchmark_prompts = [
            "What is cloud computing?",
            "Explain blockchain",
            "What is IoT?"
        ]

        for model_name in list(evaluator.models.keys())[:1]:
            latency_result = benchmark.run_latency_benchmark(model_name, benchmark_prompts[:2])
            print(f"  {model_name} - Latency:")
            print(f"    Average: {latency_result.avg_latency:.4f}s")

            cost_result = benchmark.run_cost_benchmark(model_name, benchmark_prompts[:2])
            print(f"  {model_name} - Cost:")
            print(f"    Total: ${cost_result.total_cost:.6f}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\n" + "=" * 70)
    print("Quick start complete!")
    print("\nNext steps:")
    print("  1. Review examples.py for more use cases")
    print("  2. Modify main.py to run custom evaluations")
    print("  3. Check eval_results/ directory for generated reports")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    quick_start()
