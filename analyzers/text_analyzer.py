"""
TruthLens - Text & Context Forensic Analyzer
Inspects accompanying articles, captions, social posts, and transcripts for AI-generation signatures,
stylometric homogeneity (low burstiness), sensationalist disinfo markers, and factual/temporal contradictions.
"""

import re
import math
from typing import Dict, Any, List, Tuple
from collections import Counter
import numpy as np

from core.models import (
    ModalityType,
    ForensicIndicator,
    ModalityAnalysisResult,
    IndicatorCategory,
    SeverityLevel,
    EvidenceReference,
    VerdictCategory
)
from core.hash_util import compute_file_hashes


class TextForensicAnalyzer:
    """Performs forensic linguistic, stylometric, and context analysis on accompanying text."""

    def __init__(self):
        # Stereotypical phrases heavily over-indexed in LLM outputs
        self.llm_hedges = [
            "delve into", "delves into", "testament to", "crucial to remember",
            "it is important to note", "in conclusion", "multifaceted", "beacon of",
            "tapestry of", "pivotal role", "realm of", "game-changer", "moreover",
            "furthermore", "it's essential to understand", "sheds light on", "underscore"
        ]
        # Sensationalist / disinformation amplification patterns
        self.disinfo_patterns = [
            r"share before (it is|they) delete[d]?",
            r"mainstream media won'?t show (you )?this",
            r"the truth they are hiding",
            r"proof that it was all staged",
            r"leaked confidential document",
            r"100% confirmed by insider",
            r"wake up people"
        ]

    def analyze(self, text_or_bytes: str | bytes, filename: str = "context_text.txt") -> ModalityAnalysisResult:
        if isinstance(text_or_bytes, bytes):
            text = text_or_bytes.decode("utf-8", errors="ignore")
            data_bytes = text_or_bytes
        else:
            text = str(text_or_bytes)
            data_bytes = text.encode("utf-8")

        sha256, md5, size_bytes = compute_file_hashes(data_bytes)

        indicators: List[ForensicIndicator] = []
        metrics: Dict[str, Any] = {}
        limitations: List[str] = []

        words = re.findall(r"\b[A-Za-z0-9'-]+\b", text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

        metrics["word_count"] = len(words)
        metrics["sentence_count"] = len(sentences)

        if len(words) < 25:
            limitations.append("Text snippet has fewer than 25 words; linguistic stylometry and burstiness metrics have high variance on short samples.")

        # 1. Stylometric Burstiness & Uniformity (AI vs Human)
        burstiness_metrics, burst_ind = self._analyze_burstiness(sentences, words, filename, sha256)
        metrics["stylometry"] = burstiness_metrics
        indicators.extend(burst_ind)

        # 2. LLM Hallmarking & Synthetic Phrase Frequency
        llm_metrics, llm_ind = self._detect_llm_lexicon(text, filename, sha256)
        metrics["llm_lexicon"] = llm_metrics
        indicators.extend(llm_ind)

        # 3. Disinformation / Sensationalist Framing Detection
        disinfo_metrics, disinfo_ind = self._detect_disinformation_framing(text, filename, sha256)
        metrics["disinfo_framing"] = disinfo_metrics
        indicators.extend(disinfo_ind)

        # 4. Temporal / Date and Geographic Claims Extraction
        claims_metrics = self._extract_claims_and_entities(text)
        metrics["extracted_claims"] = claims_metrics

        manip_prob, confidence, verdict = self._calibrate_text_score(indicators, len(words))

        return ModalityAnalysisResult(
            modality=ModalityType.TEXT,
            filename=filename,
            file_size_bytes=size_bytes,
            sha256=sha256,
            manipulation_probability=round(manip_prob, 3),
            confidence=round(confidence, 3),
            verdict=verdict,
            metrics=metrics,
            indicators=indicators,
            limitations=limitations,
            visualizations={}
        )

    def _analyze_burstiness(
        self, sentences: List[str], words: List[str], filename: str, sha256: str
    ) -> Tuple[Dict[str, Any], List[ForensicIndicator]]:
        """
        Human writing exhibits high variance in sentence lengths ('burstiness').
        AI generation typically shows uniform, predictable sentence lengths and low entropy.
        """
        if len(sentences) < 4:
            return {"status": "insufficient_sentences_for_burstiness"}, []

        lens = [len(s.split()) for s in sentences]
        mean_len = float(np.mean(lens)) if lens else 0.0
        std_len = float(np.std(lens)) if lens else 0.0
        # Coefficient of variation (CV = std / mean)
        cv = std_len / max(1.0, mean_len)

        # Type-Token Ratio (vocabulary diversity)
        ttr = len(set(w.lower() for w in words)) / max(1, len(words))

        indicators: List[ForensicIndicator] = []
        # AI text typically has CV < 0.25 on multi-sentence paragraphs
        if cv < 0.22 and len(sentences) >= 5:
            indicators.append(
                ForensicIndicator(
                    indicator_id="TXT_LOW_BURSTINESS_HOMOGENEITY",
                    category=IndicatorCategory.TEXT_SYNTHESIS_METRIC,
                    modality=ModalityType.TEXT,
                    title="Low Syntactic Burstiness (Uniform Sentence Lengths)",
                    description="Sentence lengths display unnatural mathematical uniformity across the entire text, a known signature of automated LLM text generation.",
                    technical_details=f"Coefficient of variation (CV): {cv:.3f} (human baseline typically > 0.45). Mean length: {mean_len:.1f} words, std: {std_len:.1f}.",
                    severity=SeverityLevel.MEDIUM,
                    suspicion_score=0.74,
                    confidence=0.76,
                    evidence_ref=EvidenceReference(
                        modality=ModalityType.TEXT,
                        source_filename=filename,
                        sha256_hash=sha256,
                        location_type="sentence_distribution",
                        location_value={"coefficient_of_variation": round(cv, 3), "mean_sentence_length": round(mean_len, 1)}
                    )
                )
            )

        metrics = {
            "mean_sentence_length": round(mean_len, 1),
            "sentence_length_std": round(std_len, 1),
            "burstiness_cv": round(cv, 3),
            "vocabulary_ttr": round(ttr, 3)
        }

        return metrics, indicators

    def _detect_llm_lexicon(
        self, text: str, filename: str, sha256: str
    ) -> Tuple[Dict[str, Any], List[ForensicIndicator]]:
        """Detects high concentrations of LLM boilerplate / cliché phrases."""
        text_lower = text.lower()
        matched_hedges = []
        flagged_spans = []

        for hedge in self.llm_hedges:
            pattern = re.compile(re.escape(hedge), re.IGNORECASE)
            for m in pattern.finditer(text):
                matched_hedges.append(hedge)
                flagged_spans.append({"span": [m.start(), m.end()], "phrase": hedge})

        indicators: List[ForensicIndicator] = []
        unique_matches = list(set(matched_hedges))

        if len(unique_matches) >= 3:
            indicators.append(
                ForensicIndicator(
                    indicator_id="TXT_LLM_CLICHE_CONCENTRATION",
                    category=IndicatorCategory.SYNTHETIC_GENERATION,
                    modality=ModalityType.TEXT,
                    title="High Density of Synthetic LLM Idioms and Boilerplate Phrasing",
                    description=f"Multiple canonical LLM phrases identified in close proximity: {unique_matches[:4]}.",
                    technical_details=f"Detected {len(matched_hedges)} occurrences of LLM marker phrases across {len(unique_matches)} distinct idiom categories.",
                    severity=SeverityLevel.HIGH,
                    suspicion_score=0.82,
                    confidence=0.84,
                    evidence_ref=EvidenceReference(
                        modality=ModalityType.TEXT,
                        source_filename=filename,
                        sha256_hash=sha256,
                        location_type="text_spans",
                        location_value={"matched_phrases": unique_matches, "occurrences": len(matched_hedges)}
                    )
                )
            )

        metrics = {
            "llm_hedge_occurrences": len(matched_hedges),
            "unique_llm_phrases": unique_matches,
            "flagged_spans": flagged_spans[:5]
        }

        return metrics, indicators

    def _detect_disinformation_framing(
        self, text: str, filename: str, sha256: str
    ) -> Tuple[Dict[str, Any], List[ForensicIndicator]]:
        """Flags deceptive / coordinated inauthentic behavior amplification hooks."""
        matched_hooks = []
        for pat in self.disinfo_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            if matches:
                matched_hooks.append(pat)

        indicators: List[ForensicIndicator] = []
        if matched_hooks:
            indicators.append(
                ForensicIndicator(
                    indicator_id="TXT_DISINFO_AMPLIFICATION_HOOK",
                    category=IndicatorCategory.TEXT_SYNTHESIS_METRIC,
                    modality=ModalityType.TEXT,
                    title="Deceptive Urgency & Disinformation Amplification Framing",
                    description="Text incorporates classic psychological urgency triggers designed to compel viral sharing prior to fact-checking.",
                    technical_details=f"Matched urgency patterns: {len(matched_hooks)}.",
                    severity=SeverityLevel.MEDIUM,
                    suspicion_score=0.68,
                    confidence=0.79,
                    evidence_ref=EvidenceReference(
                        modality=ModalityType.TEXT,
                        source_filename=filename,
                        sha256_hash=sha256,
                        location_type="disinfo_markers",
                        location_value={"patterns_count": len(matched_hooks)}
                    )
                )
            )

        metrics = {
            "urgency_triggers_count": len(matched_hooks),
            "contains_viral_hooks": bool(matched_hooks)
        }

        return metrics, indicators

    def _extract_claims_and_entities(self, text: str) -> Dict[str, Any]:
        """Extracts dates, years, locations, and proper nouns for cross-modal verification."""
        # Simple regex-based entity and date harvest
        years = re.findall(r"\b(19\d\d|20\d\d)\b", text)
        dates = re.findall(r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b", text, re.IGNORECASE)
        # Proper nouns capitalized
        proper_nouns = list(set(re.findall(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*\b", text)))

        return {
            "mentioned_years": list(set(years)),
            "mentioned_dates": dates,
            "key_entities": proper_nouns[:10]
        }

    def _calibrate_text_score(
        self, indicators: List[ForensicIndicator], word_count: int
    ) -> Tuple[float, float, VerdictCategory]:
        if not indicators:
            return 0.10, 0.80, VerdictCategory.LIKELY_AUTHENTIC

        severity_weights = {
            SeverityLevel.INFO: 0.1,
            SeverityLevel.LOW: 0.3,
            SeverityLevel.MEDIUM: 0.6,
            SeverityLevel.HIGH: 0.85,
            SeverityLevel.CRITICAL: 1.0,
        }

        weighted_sum = sum(ind.suspicion_score * severity_weights[ind.severity] for ind in indicators)
        max_possible = sum(severity_weights[ind.severity] for ind in indicators)
        score = weighted_sum / max(1e-5, max_possible)

        # Short text penalizes confidence
        len_factor = min(1.0, max(0.5, word_count / 80.0))
        avg_conf = sum(ind.confidence for ind in indicators) / len(indicators)
        final_conf = min(0.92, avg_conf * len_factor)

        if score >= 0.70:
            verdict = VerdictCategory.HIGH_PROBABILITY_MANIPULATION
        elif score >= 0.40:
            verdict = VerdictCategory.SUSPICIOUS_ANOMALIES_DETECTED
        else:
            verdict = VerdictCategory.LIKELY_AUTHENTIC

        return score, final_conf, verdict
