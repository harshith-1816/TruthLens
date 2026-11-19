"""
TruthLens - Calibrated Confidence and Evidential Fusion Scorer
Synthesizes multi-modal signals and cross-modal findings into a calibrated composite assessment
with honest uncertainty estimation, alternative explanations, and forensic human-check checklists.
"""

from typing import Dict, List, Tuple
from core.models import (
    ModalityAnalysisResult,
    CrossModalFinding,
    CalibratedAssessment,
    VerdictCategory,
    ModalityType
)


class CalibratedForensicScorer:
    """Calculates evidentially grounded composite scores with calibrated uncertainty."""

    def evaluate(
        self,
        modality_results: Dict[str, ModalityAnalysisResult],
        cross_modal_findings: List[CrossModalFinding]
    ) -> CalibratedAssessment:
        if not modality_results:
            return CalibratedAssessment(
                overall_manipulation_score=0.0,
                calibrated_confidence=0.0,
                overall_verdict=VerdictCategory.INCONCLUSIVE,
                evidential_summary="No evidence media provided for analysis.",
                modality_breakdown={},
                uncertainty_factors=["Zero modalities submitted for analysis."],
                alternative_explanations=[],
                recommended_human_checks=["Submit source evidence files to initiate forensic investigation."]
            )

        # 1. Base Modality Weighting
        # Assign base evidentiary weights: Video and Image provide direct visual pixel ground truth,
        # Audio provides biometric voice acoustics, Text provides contextual semantics
        modality_weights = {
            "image": 1.2,
            "video": 1.3,
            "audio": 1.1,
            "text": 0.8
        }

        total_weight = 0.0
        weighted_score_sum = 0.0
        conf_sum = 0.0
        modality_breakdown = {}

        for mod_name, res in modality_results.items():
            w = modality_weights.get(mod_name, 1.0)
            score_100 = res.manipulation_probability * 100.0
            modality_breakdown[mod_name] = round(score_100, 1)

            weighted_score_sum += score_100 * w * res.confidence
            total_weight += w * res.confidence
            conf_sum += res.confidence

        base_score = weighted_score_sum / max(1e-5, total_weight)
        avg_confidence = (conf_sum / len(modality_results)) * 100.0

        # 2. Cross-Modal Fusion Adjustment
        cross_modal_adjustment = 0.0
        corroboration_count = 0
        contradiction_count = 0

        for cm in cross_modal_findings:
            if cm.risk_impact == "INCREASES_RISK":
                cross_modal_adjustment += 7.5 * cm.confidence
                corroboration_count += 1
            elif cm.risk_impact == "LOWERS_RISK":
                cross_modal_adjustment -= 7.5 * cm.confidence
                corroboration_count += 1
            elif cm.status == "CONTRADICTION":
                cross_modal_adjustment += 10.0 * cm.confidence
                contradiction_count += 1

        composite_score = max(0.0, min(99.0, base_score + cross_modal_adjustment))

        # 3. Honest Uncertainty Estimation
        uncertainty_factors = []
        num_modalities = len(modality_results)

        if num_modalities == 1:
            uncertainty_factors.append(
                "Single-modality investigation: analysis is blind to cross-modal synchronization and contextual contradictions."
            )
            # Penalize confidence for single-modality
            calibrated_conf = avg_confidence * 0.82
        elif num_modalities >= 3:
            # Multi-modal triangulation increases certainty
            calibrated_conf = min(96.0, avg_confidence * 1.08)
        else:
            calibrated_conf = avg_confidence

        # Check for collected limitations across modalities
        for mod_name, res in modality_results.items():
            for lim in res.limitations:
                uncertainty_factors.append(f"[{mod_name.upper()}] {lim}")

        if contradiction_count > 0:
            uncertainty_factors.append(
                f"Cross-modal contradictions observed ({contradiction_count} conflict(s)); indicates potential multi-source splicing."
            )
            calibrated_conf *= 0.90

        # 4. Determine Overall Calibrated Verdict
        if composite_score >= 70.0 and calibrated_conf >= 60.0:
            verdict = VerdictCategory.HIGH_PROBABILITY_MANIPULATION
        elif composite_score >= 40.0:
            verdict = VerdictCategory.SUSPICIOUS_ANOMALIES_DETECTED
        elif calibrated_conf < 45.0:
            verdict = VerdictCategory.INCONCLUSIVE
        else:
            verdict = VerdictCategory.LIKELY_AUTHENTIC

        # 5. Evidential Summary Synthesis
        summary_sentences = []
        if verdict == VerdictCategory.HIGH_PROBABILITY_MANIPULATION:
            summary_sentences.append(
                f"Analysis indicates high probability of synthetic generation or malicious tampering (Forensic Score: {composite_score:.1f}/100, Calibrated Confidence: {calibrated_conf:.1f}%)."
            )
            if corroboration_count > 0:
                summary_sentences.append(
                    f"Strong cross-modal corroboration was established across {num_modalities} examined modalities."
                )
        elif verdict == VerdictCategory.SUSPICIOUS_ANOMALIES_DETECTED:
            summary_sentences.append(
                f"Multiple forensic anomalies were flagged across the evidence (Forensic Score: {composite_score:.1f}/100), but findings remain below conclusive synthetic threshold."
            )
        elif verdict == VerdictCategory.LIKELY_AUTHENTIC:
            summary_sentences.append(
                f"No persistent synthetic generation or digital splicing signatures were identified (Forensic Score: {composite_score:.1f}/100, Certainty: {calibrated_conf:.1f}%)."
            )
        else:
            summary_sentences.append(
                f"Forensic signals are ambiguous or degraded (Calibrated Certainty: {calibrated_conf:.1f}%). Unable to establish definitive authenticity baseline."
            )

        evidential_summary = " ".join(summary_sentences)

        # 6. Alternative Benign Explanations (Forensic Humility)
        alternative_explanations = self._generate_alternative_explanations(modality_results, composite_score)

        # 7. Recommended Human-in-the-Loop Forensic Checks
        recommended_human_checks = self._generate_human_checks(modality_results, verdict)

        return CalibratedAssessment(
            overall_manipulation_score=round(composite_score, 1),
            calibrated_confidence=round(calibrated_conf, 1),
            overall_verdict=verdict,
            evidential_summary=evidential_summary,
            modality_breakdown=modality_breakdown,
            uncertainty_factors=uncertainty_factors,
            alternative_explanations=alternative_explanations,
            recommended_human_checks=recommended_human_checks
        )

    def _generate_alternative_explanations(
        self, modality_results: Dict[str, ModalityAnalysisResult], score: float
    ) -> List[str]:
        alternatives = []
        if "image" in modality_results:
            alternatives.append(
                "Image compression discrepancy may originate from multi-generation social media re-compression (e.g. WhatsApp, Facebook, Twitter) rather than localized image splicing."
            )
            alternatives.append(
                "Camera sensor noise discrepancies can occasionally be induced by computational photography features (e.g. smartphone Night Mode, HDR multi-frame blending, portrait bokeh)."
            )
        if "audio" in modality_results:
            alternatives.append(
                "Acoustic frequency cutoff and low high-frequency energy may stem from standard telecommunication narrowband speech codecs (AMR 8kHz, G.711) rather than neural vocoder synthesis."
            )
            alternatives.append(
                "Pitch flatness can sometimes occur naturally with monotonous speaker cadence or aggressive noise-gate suppression plugins."
            )
        if "video" in modality_results:
            alternatives.append(
                "Temporal frame differences and jitter spikes can be triggered by network packet loss, variable frame rate (VFR) capture, or lossy video re-muxing."
            )
        if "text" in modality_results:
            alternatives.append(
                "Stylometric uniformity or formal wording in text may reflect strict institutional press release guidelines or non-native English translation rather than LLM text generation."
            )
        return alternatives[:4]

    def _generate_human_checks(
        self, modality_results: Dict[str, ModalityAnalysisResult], verdict: VerdictCategory
    ) -> List[str]:
        checks = [
            "Request the original, uncompressed camera capture files (RAW, DNG, WAV, or original MP4 camera recording) directly from the originating source.",
            "Verify the digital chain of custody and transmission logs from the primary publisher or eyewitness.",
        ]
        if "image" in modality_results:
            checks.append("Perform reverse image search (e.g. Google Lens, TinEye) to trace earliest appearance and check for prior unmanipulated versions.")
        if "audio" in modality_results:
            checks.append("Conduct biometric speaker comparison against verified reference audio samples of the alleged speaker.")
        if "video" in modality_results:
            checks.append("Perform manual frame-by-frame inspection of facial contours, earlobes, and dental alignment during rapid head turns.")
        if "text" in modality_results:
            checks.append("Cross-reference reported events and dates against official meteorological, civic, and police dispatch records.")
        return checks
