"""
TruthLens - SQLAlchemy Database Schema
Defines persistent entities for Cases, Evidence Files (with SHA-256 and MIME types),
Forensic Indicators, Cross-Modal Findings, and Chain of Custody records.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class CaseRecordDB(Base):
    """Case record storing overall investigation state and calibrated verdict."""
    __tablename__ = "cases"

    case_id = Column(String(64), primary_key=True, index=True)
    report_id = Column(String(64), unique=True, index=True)
    title = Column(String(255), nullable=False)
    investigator = Column(String(255), default="Forensic Examiner")
    overall_verdict = Column(String(64), nullable=False)
    manipulation_score = Column(Float, nullable=False)
    calibrated_confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(32), default="COMPLETED")
    evidential_summary = Column(Text, nullable=True)

    # Relationships
    evidence_files = relationship("EvidenceFileDB", back_populates="case", cascade="all, delete-orphan")
    indicators = relationship("IndicatorDB", back_populates="case", cascade="all, delete-orphan")
    cross_modal_findings = relationship("CrossModalFindingDB", back_populates="case", cascade="all, delete-orphan")
    chain_of_custody = relationship("ChainOfCustodyDB", back_populates="case", cascade="all, delete-orphan")


class EvidenceFileDB(Base):
    """Evidence file record storing cryptographic SHA-256 hash, MIME type, and storage reference."""
    __tablename__ = "evidence_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True)
    modality = Column(String(32), nullable=False)  # image, video, audio, text
    original_filename = Column(String(255), nullable=False)
    storage_key = Column(String(512), nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    mime_type = Column(String(128), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("CaseRecordDB", back_populates="evidence_files")


class IndicatorDB(Base):
    """Flagged suspicious forensic indicator record."""
    __tablename__ = "forensic_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True)
    indicator_id = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    modality = Column(String(32), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    technical_details = Column(Text, nullable=False)
    severity = Column(String(32), nullable=False)
    suspicion_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    location_type = Column(String(64), nullable=True)
    location_value_json = Column(Text, nullable=True)

    case = relationship("CaseRecordDB", back_populates="indicators")


class CrossModalFindingDB(Base):
    """Cross-modal correlation finding record."""
    __tablename__ = "cross_modal_findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True)
    finding_id = Column(String(128), nullable=False)
    correlation_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=False)
    risk_impact = Column(String(32), nullable=False)
    confidence = Column(Float, nullable=False)

    case = relationship("CaseRecordDB", back_populates="cross_modal_findings")


class ChainOfCustodyDB(Base):
    """Cryptographic chain of custody record."""
    __tablename__ = "chain_of_custody"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(String(64), nullable=False)
    event = Column(String(128), nullable=False)
    performed_by = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    sha256 = Column(String(64), nullable=False)
    notes = Column(Text, nullable=True)

    case = relationship("CaseRecordDB", back_populates="chain_of_custody")
