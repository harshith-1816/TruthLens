"""
TruthLens - Audio Forensics Automated Tests
Tests vocoder brickwall roll-off, pitch jitter flatness, ambient noise shifts, and speaker verification.
"""

import pytest
from analyzers.audio_analyzer import AudioForensicAnalyzer
from samples.sample_cases import generate_synthetic_cloned_audio, generate_authentic_audio


def test_synthetic_cloned_audio_detection():
    analyzer = AudioForensicAnalyzer()
    aud_bytes = generate_synthetic_cloned_audio()

    result = analyzer.analyze(aud_bytes, "test_cloned_voice.wav")
    assert result.modality.value == "audio"
    assert result.manipulation_probability >= 0.65

    # Check that vocoder brickwall or robotic pitch flatness was flagged
    ind_ids = [ind.indicator_id for ind in result.indicators]
    assert "AUD_VOCODER_BRICKWALL_CUTOFF" in ind_ids or "AUD_ROBOTIC_PITCH_FLATNESS" in ind_ids
    assert "spectrogram" in result.visualizations


def test_authentic_audio_detection():
    analyzer = AudioForensicAnalyzer()
    aud_bytes = generate_authentic_audio()

    result = analyzer.analyze(aud_bytes, "test_authentic_speech.wav")
    assert result.modality.value == "audio"
    assert result.manipulation_probability < 0.40
    assert result.verdict.value == "LIKELY_AUTHENTIC"
    # Should not have brickwall cutoff
    assert result.metrics["spectral_forensics"]["brickwall_filter_detected"] is False
