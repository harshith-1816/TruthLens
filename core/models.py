"""
TruthLens - Core Forensic Data Models
Pydantic schemas defining evidence sources, indicators, modality analysis,
cross-modal correlation, calibrated uncertainty, and forensic reports.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, model_validator
from datetime import datetime, timezone


def sanitize_for_json(obj: Any) -> Any:
    """Recursively converts numpy types and non-primitive objects to native Python primitives."""
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(x) for x in obj]
    elif hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            return str(obj)
    elif hasattr(obj, "tolist"):
        try:
            return obj.tolist()
        except Exception:
            return str(obj)
    return obj


class ModalityType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    METADATA = "metadata"
    CROSS_MODAL = "cross_modal"


class SeverityLevel(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IndicatorCategory(str, Enum):
    METADATA_INCONSISTENCY = "METADATA_INCONSISTENCY"
    COMPRESSION_ANOMALY = "COMPRESSION_ANOMALY"
    FREQUENCY_ARTIFACT = "FREQUENCY_ARTIFACT"
    SYNTHETIC_GENERATION = "SYNTHETIC_GENERATION"
    TEMPORAL_JITTER = "TEMPORAL_JITTER"
    VOICE_CLONING_SIGNATURE = "VOICE_CLONING_SIGNATURE"
    TEXT_SYNTHESIS_METRIC = "TEXT_SYNTHESIS_METRIC"
    CROSS_MODAL_MISMATCH = "CROSS_MODAL_MISMATCH"
    SEAM_OR_SPLICE = "SEAM_OR_SPLICE"
    NOISE_DISCREPANCY = "NOISE_DISCREPANCY"


class VerdictCategory(str, Enum):
    LIKELY_AUTHENTIC = "LIKELY_AUTHENTIC"
    SUSPICIOUS_ANOMALIES_DETECTED = "SUSPICIOUS_ANOMALIES_DETECTED"
    HIGH_PROBABILITY_MANIPULATION = "HIGH_PROBABILITY_MANIPULATION"
    INCONCLUSIVE = "INCONCLUSIVE"


class EvidenceReference(BaseModel):
    modality: ModalityType
    source_filename: str
    sha256_hash: str
    location_type: str = Field(
        ..., description="e.g., 'bounding_box', 'timestamp_range', 'frame_number', 'text_span'"
    )
    location_value: Dict[str, Any] = Field(
        default_factory=dict,
        description="Coordinates, frame numbers, timestamps, or character indices",
    )
    preview_url_or_b64: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sanitize(cls, data: Any) -> Any:
        return sanitize_for_json(data)


class ForensicIndicator(BaseModel):
    indicator_id: str
    category: IndicatorCategory
    modality: ModalityType
    title: str
    description: str
    technical_details: str
    severity: SeverityLevel
    suspicion_score: float = Field(..., ge=0.0, le=1.0, description="0.0 = pristine, 1.0 = definitely manipulated")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence of this individual detection")
    evidence_ref: Optional[EvidenceReference] = None
    corroboration_notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sanitize(cls, data: Any) -> Any:
        return sanitize_for_json(data)


class ModalityAnalysisResult(BaseModel):
    modality: ModalityType
    filename: str
    file_size_bytes: int
    sha256: str
    analyzed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    manipulation_probability: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    verdict: VerdictCategory
    metrics: Dict[str, Any] = Field(default_factory=dict)
    indicators: List[ForensicIndicator] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    visualizations: Dict[str, str] = Field(
        default_factory=dict,
        description="Keyed previews: e.g. 'ela_preview', 'fft_spectrum', 'audio_spectrogram'",
    )

    @model_validator(mode="before")
    @classmethod
    def sanitize(cls, data: Any) -> Any:
        return sanitize_for_json(data)


class CrossModalFinding(BaseModel):
    finding_id: str
    modalities_involved: List[ModalityType]
    correlation_type: str = Field(
        ...,
        description="e.g. 'AUDIO_VISUAL_LIP_SYNC', 'IMAGE_TEXT_SEMANTIC', 'TEMPORAL_METADATA_ALIGNMENT', 'SPEECH_TRANSCRIPT_CADENCE'"
    )
    status: str = Field(..., description="'CORROBORATING_AUTHENTIC', 'CORROBORATING_MANIPULATION', 'CONTRADICTION', 'INSUFFICIENT_DATA'")
    description: str
    details: str
    risk_impact: str = Field(..., description="'INCREASES_RISK', 'LOWERS_RISK', 'NEUTRAL'")
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_references: List[EvidenceReference] = Field(default_factory=list)


class CalibratedAssessment(BaseModel):
    overall_manipulation_score: float = Field(..., ge=0.0, le=100.0, description="0 to 100 composite risk score")
    calibrated_confidence: float = Field(..., ge=0.0, le=100.0, description="Calibrated certainty of the finding")
    overall_verdict: VerdictCategory
    evidential_summary: str
    modality_breakdown: Dict[str, float] = Field(default_factory=dict)
    uncertainty_factors: List[str] = Field(default_factory=list)
    alternative_explanations: List[str] = Field(default_factory=list)
    recommended_human_checks: List[str] = Field(default_factory=list)


class ChainOfCustodyRecord(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event: str
    performed_by: str
    file_name: str
    sha256: str
    notes: Optional[str] = None


class ForensicReport(BaseModel):
    report_id: str
    case_title: str
    case_id: str
    investigator: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    assessment: CalibratedAssessment
    modality_results: Dict[str, ModalityAnalysisResult] = Field(default_factory=dict)
    cross_modal_findings: List[CrossModalFinding] = Field(default_factory=list)
    all_indicators: List[ForensicIndicator] = Field(default_factory=list)
    chain_of_custody: List[ChainOfCustodyRecord] = Field(default_factory=list)
    disclaimer: str = (
        "This report is generated by the TruthLens Forensics Platform as an investigative "
        "decision-support aid. Automated forensic scores, spectral analyses, and cross-modal correlations "
        "do not constitute absolute legal proof of authenticity or manipulation. Results must be reviewed "
        "by qualified forensic examiners in accordance with applicable evidentiary standards."
    )
