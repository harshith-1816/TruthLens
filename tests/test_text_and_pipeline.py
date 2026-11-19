"""
TruthLens - Text & Cross-Modal Forensics Automated Tests
Tests stylometric burstiness, LLM idioms, disinformation urgency hooks, and cross-modal correlation.
"""

import pytest
from analyzers.text_analyzer import TextForensicAnalyzer
from analyzers.cross_modal import CrossModalCorrelator
from core.pipeline import TruthLensPipeline
from samples.sample_cases import get_sample_cases


def test_llm_disinfo_text_detection():
    analyzer = TextForensicAnalyzer()
    llm_disinfo_text = (
        "It is crucial to remember that our organization is a beacon of integrity. "
        "In conclusion, we must delve into these challenges. Furthermore, it is essential to understand "
        "that mainstream media won't show you this confidential leak. Share before they delete this!"
    )

    result = analyzer.analyze(llm_disinfo_text, "social_caption.txt")
    assert result.modality.value == "text"
    assert result.manipulation_probability >= 0.55

    ind_ids = [ind.indicator_id for ind in result.indicators]
    assert "TXT_LLM_CLICHE_CONCENTRATION" in ind_ids or "TXT_DISINFO_AMPLIFICATION_HOOK" in ind_ids


def test_end_to_end_pipeline_and_storage():
    pipeline = TruthLensPipeline()
    cases = get_sample_cases()
    deepfake_case = cases["case_deepfake_attack"]

    report = pipeline.run(
        case_title=deepfake_case["title"],
        investigator="Automated PyTest Agent",
        image_data=deepfake_case["image"],
        image_filename=deepfake_case["image_filename"],
        video_data=deepfake_case["video"],
        video_filename=deepfake_case["video_filename"],
        audio_data=deepfake_case["audio"],
        audio_filename=deepfake_case["audio_filename"],
        text_data=deepfake_case["text"],
        text_filename=deepfake_case["text_filename"],
    )

    assert report.report_id.startswith("TL-REP-")
    assert report.assessment.overall_manipulation_score > 70.0
    assert "MANIPULATION" in report.assessment.overall_verdict.value
    assert len(report.cross_modal_findings) > 0
    assert len(report.chain_of_custody) >= 4

    # Verify SHA-256 hashes recorded in custody
    for cust in report.chain_of_custody:
        assert cust.sha256 is not None
        assert len(cust.sha256) > 0
