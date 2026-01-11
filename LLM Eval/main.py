import os
import sys
from dotenv import load_dotenv
from config import ModelConfig, ModelProvider, EvalConfig
from evaluator import Evaluator
from arena import Arena
from pathlib import Path

load_dotenv()

def setup_evaluator():
    eval_config = EvalConfig()
    evaluator = Evaluator(eval_config)

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

    try:
        evaluator.register_model("Claude", claude_config)
        print("✓ Claude registered")
    except Exception as e:
        print(f"✗ Claude registration failed: {e}")

    try:
        evaluator.register_model("GPT-3.5", openai_config)
        print("✓ GPT-3.5 registered")
    except Exception as e:
        print(f"✗ GPT-3.5 registration failed: {e}")

    try:
        evaluator.register_model("Gemini", gemini_config)
        print("✓ Gemini registered")
    except Exception as e:
        print(f"✗ Gemini registration failed: {e}")

    return evaluator

def run_single_evaluation():
    print("\n" + "=" * 60)
    print("SINGLE EVALUATION")
    print("=" * 60)

    evaluator = setup_evaluator()

    if not evaluator.models:
        print("No models registered. Please set up API keys.")
        return

    prompt = "What are the benefits of machine learning in healthcare?"
    reference = "Machine learning in healthcare improves diagnosis accuracy, enables personalized treatment plans, automates administrative tasks, and facilitates drug discovery."

    for model_name in list(evaluator.models.keys())[:1]:
        print(f"\nEvaluating {model_name}...")

        try:
            result = evaluator.evaluate_single(model_name, prompt, reference)

            print(f"Response: {result.response.text[:100]}...")
            print(f"Latency: {result.response.latency:.2f}s")
            print(f"Cost: ${result.response.cost:.6f}")

            if result.metrics:
                for metric_name, metric in result.metrics.items():
                    print(f"{metric_name}: {metric.score:.4f}")
        except Exception as e:
            print(f"Error evaluating {model_name}: {e}")

def run_batch_evaluation():
    print("\n" + "=" * 60)
    print("BATCH EVALUATION")
    print("=" * 60)

    evaluator = setup_evaluator()

    if not evaluator.models:
        print("No models registered.")
        return

    prompts = [
        "What is artificial intelligence?",
        "Explain quantum computing",
        "How does photosynthesis work?"
    ]

    references = [
        "Artificial intelligence refers to machines that can perform tasks that typically require human intelligence.",
        "Quantum computing uses quantum bits or qubits instead of classical bits.",
        "Photosynthesis is the process where plants convert light into chemical energy."
    ]

    for model_name in list(evaluator.models.keys())[:1]:
        print(f"\nBatch evaluating {model_name}...")

        try:
            results = evaluator.evaluate_batch(model_name, prompts, references)
            print(f"Evaluated {len(results)} prompts")

            summary = evaluator.get_summary_stats()
            if model_name in summary:
                stats = summary[model_name]
                print(f"Avg Latency: {stats['avg_latency']:.2f}s")
                print(f"Total Cost: ${stats['total_cost']:.6f}")
                print(f"Avg BLEU: {stats['avg_bleu']:.4f}")
                print(f"Avg ROUGE: {stats['avg_rouge']:.4f}")
                print(f"Avg BERTScore: {stats['avg_bertscore']:.4f}")
        except Exception as e:
            print(f"Error in batch evaluation: {e}")

def run_arena_evaluation():
    print("\n" + "=" * 60)
    print("ARENA EVALUATION")
    print("=" * 60)

    evaluator = setup_evaluator()

    if len(evaluator.models) < 2:
        print("Need at least 2 models for arena evaluation.")
        return

    prompts = [
        "What is the importance of biodiversity?",
        "How do neural networks learn?",
        "Explain cryptocurrency to a beginner"
    ]

    references = [
        "Biodiversity is crucial for ecosystem stability, resilience, and human survival.",
        "Neural networks learn through backpropagation and gradient descent optimization.",
        "Cryptocurrency is digital money secured by cryptography, operating on blockchain technology."
    ]

    arena = Arena(evaluator)

    print("\nRunning tournament...")
    try:
        rankings = arena.run_tournament(prompts, references)

        print("\nTournament Results:")
        for model, win_rate in sorted(rankings.items(), key=lambda x: x[1], reverse=True):
            print(f"  {model}: {win_rate:.2%}")

        arena.export_arena_report("eval_results/arena")
        print("\nArena report exported to eval_results/arena/")
    except Exception as e:
        print(f"Error in arena evaluation: {e}")

def run_cost_analysis():
    print("\n" + "=" * 60)
    print("COST ANALYSIS")
    print("=" * 60)

    evaluator = setup_evaluator()

    if not evaluator.models:
        print("No models registered.")
        return

    prompts = [
        "Tell me a story about space exploration",
        "Explain the stock market",
        "What are renewable energy sources?"
    ]

    for model_name in list(evaluator.models.keys())[:1]:
        print(f"\nCost analysis for {model_name}...")

        try:
            evaluator.evaluate_batch(model_name, prompts)

            summary = evaluator.get_summary_stats()
            if model_name in summary:
                stats = summary[model_name]
                print(f"Total Cost: ${stats['total_cost']:.6f}")
                print(f"Cost per Prompt: ${stats['total_cost'] / stats['count']:.6f}")
        except Exception as e:
            print(f"Error: {e}")

def run_toxicity_check():
    print("\n" + "=" * 60)
    print("TOXICITY CHECK")
    print("=" * 60)

    evaluator = setup_evaluator()

    if not evaluator.models:
        print("No models registered.")
        return

    prompts = [
        "What is love?",
        "Describe a beautiful sunset",
        "Explain machine learning"
    ]

    for model_name in list(evaluator.models.keys())[:1]:
        print(f"\nToxicity check for {model_name}...")

        try:
            results = evaluator.evaluate_batch(model_name, prompts)

            for result in results:
                if result.metrics and 'toxicity' in result.metrics:
                    toxicity_score = result.metrics['toxicity'].score
                    print(f"Toxicity Score: {toxicity_score:.4f}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("=" * 60)
    print("LLM EVALUATION FRAMEWORK")
    print("=" * 60)

    print("\nAvailable Evaluation Modes:")
    print("1. Single Evaluation")
    print("2. Batch Evaluation")
    print("3. Arena Comparison")
    print("4. Cost Analysis")
    print("5. Toxicity Check")
    print("6. Run All")

    choice = input("\nSelect mode (1-6): ").strip()

    if choice == "1":
        run_single_evaluation()
    elif choice == "2":
        run_batch_evaluation()
    elif choice == "3":
        run_arena_evaluation()
    elif choice == "4":
        run_cost_analysis()
    elif choice == "5":
        run_toxicity_check()
    elif choice == "6":
        run_single_evaluation()
        run_batch_evaluation()
        run_cost_analysis()
        run_toxicity_check()
        run_arena_evaluation()
    else:
        print("Invalid choice")

    print("\n" + "=" * 60)
    print("Evaluation complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
