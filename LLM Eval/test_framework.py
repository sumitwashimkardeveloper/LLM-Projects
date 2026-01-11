import unittest
from metrics import (
    BLEUMetric, ROUGEMetric, BERTScoreMetric, HallucinationDetector,
    FaithfulnessDetector, ToxicityDetector, MetricsEngine
)
from config import ModelConfig, ModelProvider, EvalConfig
from evaluator import Evaluator
from utils import DataProcessor, StatisticsCalculator, ComparisonAnalyzer

class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.bleu = BLEUMetric()
        self.rouge = ROUGEMetric()
        self.bertscore = BERTScoreMetric()
        self.hallucination = HallucinationDetector()
        self.faithfulness = FaithfulnessDetector()
        self.toxicity = ToxicityDetector()

    def test_bleu_metric(self):
        reference = "The quick brown fox jumps over the lazy dog"
        hypothesis = "The quick brown fox jumps over the lazy dog"

        result = self.bleu.compute(reference, hypothesis)

        self.assertEqual(result.name, "BLEU")
        self.assertGreater(result.score, 0.9)

    def test_rouge_metric(self):
        reference = "Machine learning enables systems to learn from data"
        hypothesis = "Machine learning helps systems to learn from data"

        result = self.rouge.compute(reference, hypothesis)

        self.assertEqual(result.name, "ROUGE")
        self.assertGreater(result.score, 0.5)
        self.assertIn("rouge1", result.details)

    def test_hallucination_detection(self):
        reference = "Paris is the capital of France"
        hypothesis = "Paris is the capital of France and has the Eiffel Tower"

        result = self.hallucination.compute(reference, hypothesis)

        self.assertEqual(result.name, "Hallucination")
        self.assertLess(result.score, 1.0)

    def test_faithfulness(self):
        reference = "Python is a programming language"
        hypothesis = "Python is a snake"
        context = "Python is a high-level programming language"

        result = self.faithfulness.compute(reference, hypothesis, context)

        self.assertEqual(result.name, "Faithfulness")
        self.assertGreaterEqual(result.score, 0.0)
        self.assertLessEqual(result.score, 1.0)

    def test_toxicity(self):
        text_clean = "This is a great program"
        text_toxic = "This is a bad and terrible implementation"

        result_clean = self.toxicity.compute(text_clean)
        result_toxic = self.toxicity.compute(text_toxic)

        self.assertGreater(result_clean.score, result_toxic.score)

    def test_metrics_engine(self):
        engine = MetricsEngine()
        reference = "Machine learning is powerful"
        hypothesis = "Machine learning is very powerful"

        results = engine.compute_all(reference, hypothesis)

        self.assertIn("bleu", results)
        self.assertIn("rouge", results)
        self.assertIn("hallucination", results)
        self.assertIn("faithfulness", results)
        self.assertIn("toxicity", results)

class TestEvaluator(unittest.TestCase):
    def test_evaluator_initialization(self):
        eval_config = EvalConfig()
        evaluator = Evaluator(eval_config)

        self.assertIsNotNone(evaluator)
        self.assertEqual(len(evaluator.models), 0)
        self.assertEqual(len(evaluator.results), 0)

    def test_evaluator_model_registration(self):
        evaluator = Evaluator()

        claude_config = ModelConfig(
            provider=ModelProvider.CLAUDE,
            model_name="claude-3-haiku-20240307"
        )

        evaluator.register_model("TestModel", claude_config)

        self.assertIn("TestModel", evaluator.models)

class TestUtils(unittest.TestCase):
    def test_statistics_calculator(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]

        mean = StatisticsCalculator.calculate_mean(values)
        median = StatisticsCalculator.calculate_median(values)
        stdev = StatisticsCalculator.calculate_stdev(values)

        self.assertEqual(mean, 3.0)
        self.assertEqual(median, 3.0)
        self.assertGreater(stdev, 0)

    def test_percentile_calculation(self):
        values = list(range(1, 101))

        p50 = StatisticsCalculator.calculate_percentile(values, 50)
        p95 = StatisticsCalculator.calculate_percentile(values, 95)

        self.assertLess(p50, p95)

    def test_comparison_analyzer(self):
        results = {
            "Model A": [0.8, 0.85, 0.9],
            "Model B": [0.7, 0.75, 0.8]
        }

        analysis = ComparisonAnalyzer.compare_metrics(results)

        self.assertIn("Model A", analysis)
        self.assertIn("Model B", analysis)
        self.assertIn("mean", analysis["Model A"])
        self.assertIn("stdev", analysis["Model A"])

    def test_ranking(self):
        metrics = {"Model A": 0.9, "Model B": 0.7, "Model C": 0.8}

        ranking = ComparisonAnalyzer.rank_models(metrics)

        self.assertEqual(ranking[0][0], "Model A")
        self.assertEqual(ranking[1][0], "Model C")
        self.assertEqual(ranking[2][0], "Model B")

class TestDataProcessor(unittest.TestCase):
    def test_json_save_load(self):
        test_data = {"key": "value", "number": 123}
        filepath = "test_cache/test.json"

        DataProcessor.save_json(test_data, filepath)
        loaded_data = DataProcessor.load_json(filepath)

        self.assertEqual(loaded_data["key"], "value")
        self.assertEqual(loaded_data["number"], 123)

    def test_csv_save_load(self):
        test_data = [
            {"name": "Model A", "score": "0.9"},
            {"name": "Model B", "score": "0.8"}
        ]
        filepath = "test_cache/test.csv"

        DataProcessor.save_csv(test_data, filepath)
        loaded_data = DataProcessor.load_csv(filepath)

        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["name"], "Model A")

class TestConfig(unittest.TestCase):
    def test_model_config(self):
        config = ModelConfig(
            provider=ModelProvider.CLAUDE,
            model_name="claude-3-haiku-20240307"
        )

        self.assertEqual(config.provider, ModelProvider.CLAUDE)
        self.assertEqual(config.model_name, "claude-3-haiku-20240307")
        self.assertEqual(config.temperature, 0.7)

    def test_eval_config(self):
        config = EvalConfig()

        self.assertEqual(config.batch_size, 32)
        self.assertEqual(config.num_workers, 4)
        self.assertTrue(config.cache_responses)

def run_tests():
    print("\n" + "=" * 70)
    print("RUNNING FRAMEWORK TESTS")
    print("=" * 70 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestEvaluator))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
    else:
        print(f"✗ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70 + "\n")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
