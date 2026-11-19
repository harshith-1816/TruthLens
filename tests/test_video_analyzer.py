"""
TruthLens - Video Forensics Automated Tests
Tests MP4 container inspection, temporal frame difference jitter, landmark instability, and biological signals.
"""

import pytest
from analyzers.video_analyzer import VideoForensicAnalyzer
from samples.sample_cases import generate_synthetic_video_payload


def test_synthetic_video_jitter_detection():
    analyzer = VideoForensicAnalyzer()
    vid_bytes = generate_synthetic_video_payload()

    result = analyzer.analyze(vid_bytes, "test_deepfake_jitter.gif")
    assert result.modality.value == "video"
    assert result.metrics["frames_analyzed"] >= 10

    # Ensure temporal variance was calculated
    temp_metrics = result.metrics["temporal_consistency"]
    assert "mean_interframe_mse" in temp_metrics
    assert "max_interframe_mse" in temp_metrics

    # Check temporal jitter indicator
    ind_ids = [ind.indicator_id for ind in result.indicators]
    assert any("TEMPORAL_JITTER" in ind_id for ind_id in ind_ids)
    assert "temporal_variance_timeline" in result.visualizations
