import numpy as np
from typing import List, Dict, Tuple
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score as bert_score
import nltk
from dataclasses import dataclass

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

@dataclass
class MetricResult:
    name: str
    score: float
    details: Dict = None

class BLEUMetric:
    def __init__(self):
        self.smooth_func = SmoothingFunction().method1

    def compute(self, reference: str, hypothesis: str, weights=(0.25, 0.25, 0.25, 0.25)) -> MetricResult:
        ref_tokens = nltk.word_tokenize(reference.lower())
        hyp_tokens = nltk.word_tokenize(hypothesis.lower())

        score = sentence_bleu([ref_tokens], hyp_tokens, weights=weights, smoothing_function=self.smooth_func)

        return MetricResult(
            name="BLEU",
            score=float(score),
            details={"reference_length": len(ref_tokens), "hypothesis_length": len(hyp_tokens)}
        )

class ROUGEMetric:
    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    def compute(self, reference: str, hypothesis: str) -> MetricResult:
        scores = self.scorer.score(reference, hypothesis)

        rouge_scores = {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }

        avg_score = np.mean(list(rouge_scores.values()))

        return MetricResult(
            name="ROUGE",
            score=float(avg_score),
            details=rouge_scores
        )

class BERTScoreMetric:
    def compute(self, reference: str, hypothesis: str) -> MetricResult:
        try:
            P, R, F1 = bert_score([hypothesis], [reference], lang='en', verbose=False)
            f1_score = F1[0].item()

            return MetricResult(
                name="BERTScore",
                score=float(f1_score),
                details={
                    "precision": float(P[0].item()),
                    "recall": float(R[0].item()),
                    "f1": float(f1_score)
                }
            )
        except Exception as e:
            return MetricResult(name="BERTScore", score=0.0, details={"error": str(e)})

class HallucinationDetector:
    def __init__(self):
        self.hallucination_keywords = [
            "i don't know", "i'm not sure", "unclear", "ambiguous",
            "it appears", "it seems", "possibly", "might be", "could be"
        ]

    def compute(self, reference: str, hypothesis: str) -> MetricResult:
        hyp_lower = hypothesis.lower()

        hallucination_score = 0.0
        contradictions = 0
        uncertainties = 0

        for keyword in self.hallucination_keywords:
            if keyword in hyp_lower:
                uncertainties += 1

        ref_tokens = set(nltk.word_tokenize(reference.lower()))
        hyp_tokens = set(nltk.word_tokenize(hypothesis.lower()))

        unique_hyp = hyp_tokens - ref_tokens
        if len(hyp_tokens) > 0:
            hallucination_ratio = len(unique_hyp) / len(hyp_tokens)
        else:
            hallucination_ratio = 0.0

        hallucination_score = min(1.0, hallucination_ratio + (uncertainties * 0.05))

        return MetricResult(
            name="Hallucination",
            score=1.0 - hallucination_score,
            details={
                "hallucination_ratio": float(hallucination_ratio),
                "uncertainty_markers": uncertainties,
                "contradictions": contradictions
            }
        )

class FaithfulnessDetector:
    def compute(self, reference: str, hypothesis: str, context: str = "") -> MetricResult:
        ref_tokens = set(nltk.word_tokenize(reference.lower()))
        hyp_tokens = set(nltk.word_tokenize(hypothesis.lower()))
        context_tokens = set(nltk.word_tokenize(context.lower())) if context else set()

        all_valid_tokens = ref_tokens | context_tokens

        faithful_tokens = sum(1 for token in hyp_tokens if token in all_valid_tokens)

        if len(hyp_tokens) > 0:
            faithfulness_score = faithful_tokens / len(hyp_tokens)
        else:
            faithfulness_score = 0.0

        return MetricResult(
            name="Faithfulness",
            score=float(faithfulness_score),
            details={
                "faithful_tokens": faithful_tokens,
                "total_tokens": len(hyp_tokens),
                "context_coverage": len(hyp_tokens & context_tokens) / len(hyp_tokens) if len(hyp_tokens) > 0 else 0.0
            }
        )

class ToxicityDetector:
    def __init__(self):
        self.toxic_words = [
            "hate", "bad", "terrible", "awful", "disgusting", "pathetic",
            "stupid", "idiot", "dumb", "racist", "sexist", "offensive"
        ]
        self.harmful_patterns = [
            "should", "must", "have to", "forced to"
        ]

    def compute(self, text: str) -> MetricResult:
        text_lower = text.lower()

        toxic_count = sum(1 for word in self.toxic_words if word in text_lower)
        harmful_count = sum(1 for pattern in self.harmful_patterns if pattern in text_lower)

        text_length = len(nltk.word_tokenize(text))

        if text_length > 0:
            toxicity_score = min(1.0, (toxic_count * 0.5 + harmful_count * 0.3) / text_length)
        else:
            toxicity_score = 0.0

        return MetricResult(
            name="Toxicity",
            score=1.0 - toxicity_score,
            details={
                "toxic_words_found": toxic_count,
                "harmful_patterns_found": harmful_count,
                "text_length": text_length
            }
        )

class MetricsEngine:
    def __init__(self):
        self.bleu = BLEUMetric()
        self.rouge = ROUGEMetric()
        self.bertscore = BERTScoreMetric()
        self.hallucination = HallucinationDetector()
        self.faithfulness = FaithfulnessDetector()
        self.toxicity = ToxicityDetector()

    def compute_all(self, reference: str, hypothesis: str, context: str = "") -> Dict[str, MetricResult]:
        results = {}

        results['bleu'] = self.bleu.compute(reference, hypothesis)
        results['rouge'] = self.rouge.compute(reference, hypothesis)
        results['bertscore'] = self.bertscore.compute(reference, hypothesis)
        results['hallucination'] = self.hallucination.compute(reference, hypothesis)
        results['faithfulness'] = self.faithfulness.compute(reference, hypothesis, context)
        results['toxicity'] = self.toxicity.compute(hypothesis)

        return results
