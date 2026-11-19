"""
TruthLens - Image Forensics Automated Tests
Tests EXIF parsing, ELA, 2D FFT periodic peaks, local noise Z-scores, and lighting analysis.
"""

import pytest
import io
import numpy as np
from PIL import Image
from analyzers.image_analyzer import ImageForensicAnalyzer
from samples.sample_cases import generate_synthetic_image, generate_spliced_image, generate_authentic_image


def test_synthetic_image_detection():
    analyzer = ImageForensicAnalyzer()
    img_bytes = generate_synthetic_image()

    result = analyzer.analyze(img_bytes, "test_synthetic.png")
    assert result.modality.value == "image"
    assert result.manipulation_probability >= 0.70
    assert "HIGH_PROBABILITY_MANIPULATION" in result.verdict.value

    # Check that synthetic indicators were triggered
    ind_categories = [ind.category.value for ind in result.indicators]
    assert "SYNTHETIC_GENERATION" in ind_categories or "FREQUENCY_ARTIFACT" in ind_categories
    assert "fft_spectrum" in result.visualizations


def test_spliced_image_detection():
    analyzer = ImageForensicAnalyzer()
    img_bytes = generate_spliced_image()

    result = analyzer.analyze(img_bytes, "test_spliced.jpg")
    assert result.modality.value == "image"
    assert result.manipulation_probability >= 0.50

    ind_categories = [ind.category.value for ind in result.indicators]
    assert "COMPRESSION_ANOMALY" in ind_categories or "NOISE_DISCREPANCY" in ind_categories or "METADATA_INCONSISTENCY" in ind_categories
    assert "ela_map" in result.visualizations


def test_authentic_image_detection():
    analyzer = ImageForensicAnalyzer()
    img_bytes = generate_authentic_image()

    result = analyzer.analyze(img_bytes, "test_authentic.jpg")
    assert result.modality.value == "image"
    assert result.manipulation_probability < 0.40
    assert result.verdict.value == "LIKELY_AUTHENTIC"
    assert result.metrics["metadata"]["exif_present"] is True
