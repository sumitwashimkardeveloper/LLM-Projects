import os
from dotenv import load_dotenv
from config import ModelConfig, ModelProvider, EvalConfig
from evaluator import Evaluator
from arena import Arena

load_dotenv()

def example_basic_evaluation():
    print("=" * 60)
    print("EXAMPLE 1: Basic Evaluation")
    print("=" * 60)

    eval_config = EvalConfig()
    evaluator = Evaluator(eval_config)

    claude_config = ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_name="claude-3-haiku-20240307",
        api_key=os.getenv("ANTHROPIC_API_KEY", "")
    )

    try:
        evaluator.register_model("Claude-Haiku", claude_config)

        prompt = "Summarize quantum computing in one sentence."
        reference = "Quantum computing uses quantum bits (qubits) that exploit superposition and entanglement to process information exponentially faster than classical computers."

        result = evaluator.evaluate_single("Claude-Haiku", prompt, reference)

        print(f"Model Response: {result.response.text}")
        print(f"Latency: {result.response.latency:.3f}s")
        print(f"Cost: ${result.response.cost:.6f}")

        for metric_name, metric in result.metrics.items():
            print(f"{metric_name}: {metric.score:.4f}")

    except Exception as e:
        print(f"Error: {e}")

def example_multi_model_comparison():
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Multi-Model Comparison")
    print("=" * 60)

    evaluator = Evaluator()

    models_config = {
        "Claude": ModelConfig(
            provider=ModelProvider.CLAUDE,
            model_name="claude-3-haiku-20240307",
            api_key=os.getenv("ANTHROPIC_API_KEY", "")
        ),
        "GPT-3.5": ModelConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "")
        ),
    }

    for model_name, config in models_config.items():
        try:
            evaluator.register_model(model_name, config)
            print(f"✓ {model_name} registered")
        except Exception as e:
            print(f"✗ {model_name} failed: {e}")

    if not evaluator.models:
        print("No models available")
        return

    prompt = "What is the capital of France?"
    reference = "The capital of France is Paris."

    results = evaluator.evaluate_multiple_models(list(evaluator.models.keys()), prompt, reference)

    print("\nComparison Results:")
    for model_name, result in results.items():
        print(f"\n{model_name}:")
        print(f"  Response: {result.response.text[:50]}...")
        print(f"  Latency: {result.response.latency:.3f}s")
        print(f"  Cost: ${result.response.cost:.6f}")

def example_batch_evaluation():
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Batch Evaluation")
    print("=" * 60)

    evaluator = Evaluator()

    claude_config = ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_name="claude-3-haiku-20240307",
        api_key=os.getenv("ANTHROPIC_API_KEY", "")
    )

    try:
        evaluator.register_model("Claude", claude_config)

        prompts = [
            "What is machine learning?",
            "Explain deep learning",
            "What are neural networks?"
        ]

        references = [
            "Machine learning is a subset of AI where systems learn from data without explicit programming.",
            "Deep learning uses multiple layers of neural networks to process complex patterns.",
            "Neural networks are computational models inspired by biological neurons."
        ]

        results = evaluator.evaluate_batch("Claude", prompts, references)

        print(f"Processed {len(results)} prompts")

        summary = evaluator.get_summary_stats()
        for model_name, stats in summary.items():
            print(f"\n{model_name} Statistics:")
            print(f"  Count: {stats['count']}")
            print(f"  Avg Latency: {stats['avg_latency']:.3f}s")
            print(f"  Total Cost: ${stats['total_cost']:.6f}")
            print(f"  Avg BLEU: {stats['avg_bleu']:.4f}")
            print(f"  Avg ROUGE: {stats['avg_rouge']:.4f}")
            print(f"  Avg BERTScore: {stats['avg_bertscore']:.4f}")
            print(f"  Avg Hallucination Score: {stats['avg_hallucination']:.4f}")
            print(f"  Avg Faithfulness: {stats['avg_faithfulness']:.4f}")
            print(f"  Avg Toxicity: {stats['avg_toxicity']:.4f}")

        evaluator.generate_report("eval_results")
        print("\nResults exported to eval_results/")

    except Exception as e:
        print(f"Error: {e}")

def example_arena_tournament():
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Arena Tournament")
    print("=" * 60)

    evaluator = Evaluator()

    models = {
        "Claude": ModelConfig(
            provider=ModelProvider.CLAUDE,
            model_name="claude-3-haiku-20240307",
            api_key=os.getenv("ANTHROPIC_API_KEY", "")
        ),
        "GPT-3.5": ModelConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "")
        ),
    }

    for model_name, config in models.items():
        try:
            evaluator.register_model(model_name, config)
        except Exception as e:
            print(f"Warning: {model_name} not available: {e}")

    if len(evaluator.models) < 2:
        print("Need at least 2 models for tournament")
        return

    prompts = [
        "What is artificial intelligence?",
        "Explain blockchain technology",
        "How does photosynthesis work?",
        "What is the internet of things?",
        "Describe cryptocurrency"
    ]

    references = [
        "AI is the simulation of human intelligence by machines.",
        "Blockchain is a distributed ledger technology securing transactions.",
        "Photosynthesis converts light into chemical energy in plants.",
        "IoT is a network of interconnected physical devices.",
        "Cryptocurrency is digital currency secured by cryptography."
    ]

    arena = Arena(evaluator)

    try:
        rankings = arena.run_tournament(prompts, references)

        print("\nTournament Rankings:")
        for i, (model, win_rate) in enumerate(sorted(rankings.items(), key=lambda x: x[1], reverse=True), 1):
            print(f"{i}. {model}: {win_rate:.1%}")

        arena.export_arena_report("eval_results/arena_example")
        print("\nArena report saved to eval_results/arena_example/")

    except Exception as e:
        print(f"Error: {e}")

def example_head_to_head():
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Head-to-Head Comparison")
    print("=" * 60)

    evaluator = Evaluator()

    models = {
        "Claude": ModelConfig(
            provider=ModelProvider.CLAUDE,
            model_name="claude-3-haiku-20240307",
            api_key=os.getenv("ANTHROPIC_API_KEY", "")
        ),
        "GPT-3.5": ModelConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "")
        ),
    }

    for model_name, config in models.items():
        try:
            evaluator.register_model(model_name, config)
        except Exception as e:
            print(f"Warning: {model_name} not available")

    if len(evaluator.models) < 2:
        print("Need at least 2 models")
        return

    prompts = [
        "What is machine learning?",
        "Explain neural networks",
        "How does NLP work?"
    ]

    references = [
        "Machine learning enables systems to learn from data.",
        "Neural networks process information through interconnected nodes.",
        "NLP processes and understands human language."
    ]

    arena = Arena(evaluator)
    model_list = list(evaluator.models.keys())

    try:
        result = arena.get_head_to_head(model_list[0], model_list[1], prompts, references)

        print(f"\n{result['model_a']} vs {result['model_b']}")
        print(f"Wins: {result['wins_a']} vs {result['wins_b']}")
        print(f"Win Rate: {result['win_rate_a']:.1%} vs {result['win_rate_b']:.1%}")
        print(f"Avg Latency: {result['avg_latency_a']:.3f}s vs {result['avg_latency_b']:.3f}s")
        print(f"Avg Cost: ${result['avg_cost_a']:.6f} vs ${result['avg_cost_b']:.6f}")

    except Exception as e:
        print(f"Error: {e}")

def example_hallucination_detection():
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Hallucination Detection")
    print("=" * 60)

    evaluator = Evaluator()

    claude_config = ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_name="claude-3-haiku-20240307",
        api_key=os.getenv("ANTHROPIC_API_KEY", "")
    )

    try:
        evaluator.register_model("Claude", claude_config)

        prompt = "Who invented electricity?"
        reference = "Benjamin Franklin and Thomas Edison made major contributions to electricity development."

        result = evaluator.evaluate_single("Claude", prompt, reference)

        if 'hallucination' in result.metrics:
            hallucination_metric = result.metrics['hallucination']
            print(f"Hallucination Score: {hallucination_metric.score:.4f}")
            print(f"Details: {hallucination_metric.details}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\nLLM Evaluation Framework - Examples")
    print("=" * 60)

    example_basic_evaluation()
    example_batch_evaluation()
    example_multi_model_comparison()
    example_arena_tournament()
    example_head_to_head()
    example_hallucination_detection()
