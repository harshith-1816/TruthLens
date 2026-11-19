"""
TruthLens - Master Forensic Orchestration Pipeline
Implements the 5-step workflow:
1. INGEST -> 2. ANALYZE -> 3. CORRELATE -> 4. REVIEW & CALIBRATE -> 5. REPORT
Integrated with MinIO/S3 object storage and PostgreSQL / SQLite database persistence.
"""

import uuid
import json
from typing import Dict, List, Optional, Any
from core.models import (
    ForensicReport,
    ChainOfCustodyRecord,
    ModalityAnalysisResult
)
from core.hash_util import compute_file_hashes, create_custody_record
from analyzers.image_analyzer import ImageForensicAnalyzer
from analyzers.video_analyzer import VideoForensicAnalyzer
from analyzers.audio_analyzer import AudioForensicAnalyzer
from analyzers.text_analyzer import TextForensicAnalyzer
from analyzers.cross_modal import CrossModalCorrelator
from analyzers.calibrated_scorer import CalibratedForensicScorer
from reporting.report_generator import ForensicReportGenerator
from storage.object_store import storage_service
from database.db import SessionLocal, init_db
from database.models import (
    CaseRecordDB,
    EvidenceFileDB,
    IndicatorDB,
    CrossModalFindingDB,
    ChainOfCustodyDB
)


class TruthLensPipeline:
    """Master pipeline executing multimodal digital forensic analysis."""

    def __init__(self):
        self.image_analyzer = ImageForensicAnalyzer()
        self.video_analyzer = VideoForensicAnalyzer()
        self.audio_analyzer = AudioForensicAnalyzer()
        self.text_analyzer = TextForensicAnalyzer()
        self.correlator = CrossModalCorrelator()
        self.scorer = CalibratedForensicScorer()
        self.report_generator = ForensicReportGenerator()
        # Ensure database tables exist
        try:
            init_db()
        except Exception:
            pass

    def run(
        self,
        case_title: str = "Multimodal Evidence Authenticity Review",
        investigator: str = "Forensic Examiner (TruthLens)",
        image_data: Optional[bytes | str] = None,
        image_filename: str = "evidence_image.jpg",
        video_data: Optional[bytes | str] = None,
        video_filename: str = "evidence_video.mp4",
        audio_data: Optional[bytes | str] = None,
        audio_filename: str = "evidence_audio.wav",
        reference_audio_data: Optional[bytes | str] = None,
        text_data: Optional[str | bytes] = None,
        text_filename: str = "evidence_text.txt",
        case_id: Optional[str] = None
    ) -> ForensicReport:
        active_case_id = case_id or f"CASE-{uuid.uuid4().hex[:8].upper()}"
        custody_records: List[ChainOfCustodyRecord] = []
        modality_results: Dict[str, ModalityAnalysisResult] = []
        modality_results = {}
        stored_evidence_records = []

        # ----------------- STEP 1: INGEST -----------------
        # Validate, store in MinIO/S3 object store with SHA-256 and MIME-type, register chain-of-custody
        if image_data:
            img_bytes = image_data if isinstance(image_data, bytes) else open(image_data, "rb").read()
            stored = storage_service.store_file(img_bytes, image_filename, active_case_id, "image")
            stored_evidence_records.append(stored)
            custody_records.append(
                create_custody_record(
                    "INGEST_IMAGE",
                    image_filename,
                    stored["sha256"],
                    notes=f"Stored in {stored['storage_backend']} with MIME {stored['mime_type']}"
                )
            )

        if video_data:
            vid_bytes = video_data if isinstance(video_data, bytes) else open(video_data, "rb").read()
            stored = storage_service.store_file(vid_bytes, video_filename, active_case_id, "video")
            stored_evidence_records.append(stored)
            custody_records.append(
                create_custody_record(
                    "INGEST_VIDEO",
                    video_filename,
                    stored["sha256"],
                    notes=f"Stored in {stored['storage_backend']} with MIME {stored['mime_type']}"
                )
            )

        if audio_data:
            aud_bytes = audio_data if isinstance(audio_data, bytes) else open(audio_data, "rb").read()
            stored = storage_service.store_file(aud_bytes, audio_filename, active_case_id, "audio")
            stored_evidence_records.append(stored)
            custody_records.append(
                create_custody_record(
                    "INGEST_AUDIO",
                    audio_filename,
                    stored["sha256"],
                    notes=f"Stored in {stored['storage_backend']} with MIME {stored['mime_type']}"
                )
            )

        if text_data:
            t_bytes = text_data.encode("utf-8") if isinstance(text_data, str) else text_data
            stored = storage_service.store_file(t_bytes, text_filename, active_case_id, "text")
            stored_evidence_records.append(stored)
            custody_records.append(
                create_custody_record(
                    "INGEST_TEXT_CONTEXT",
                    text_filename,
                    stored["sha256"],
                    notes=f"Stored in {stored['storage_backend']} with MIME {stored['mime_type']}"
                )
            )

        # ----------------- STEP 2: ANALYZE -----------------
        if image_data:
            modality_results["image"] = self.image_analyzer.analyze(image_data, image_filename)
            custody_records.append(
                create_custody_record(
                    "COMPLETED_IMAGE_FORENSICS",
                    image_filename,
                    modality_results["image"].sha256,
                    notes=f"Verdict: {modality_results['image'].verdict.value}, Indicators: {len(modality_results['image'].indicators)}"
                )
            )

        if video_data:
            modality_results["video"] = self.video_analyzer.analyze(video_data, video_filename)
            custody_records.append(
                create_custody_record(
                    "COMPLETED_VIDEO_FORENSICS",
                    video_filename,
                    modality_results["video"].sha256,
                    notes=f"Verdict: {modality_results['video'].verdict.value}, Indicators: {len(modality_results['video'].indicators)}"
                )
            )

        if audio_data:
            ref_bytes = None
            if reference_audio_data:
                ref_bytes = reference_audio_data if isinstance(reference_audio_data, bytes) else open(reference_audio_data, "rb").read()
            modality_results["audio"] = self.audio_analyzer.analyze(
                audio_data,
                audio_filename,
                reference_audio_bytes=ref_bytes
            )
            custody_records.append(
                create_custody_record(
                    "COMPLETED_AUDIO_FORENSICS",
                    audio_filename,
                    modality_results["audio"].sha256,
                    notes=f"Verdict: {modality_results['audio'].verdict.value}, Indicators: {len(modality_results['audio'].indicators)}"
                )
            )

        if text_data:
            modality_results["text"] = self.text_analyzer.analyze(text_data, text_filename)
            custody_records.append(
                create_custody_record(
                    "COMPLETED_TEXT_FORENSICS",
                    text_filename,
                    modality_results["text"].sha256,
                    notes=f"Verdict: {modality_results['text'].verdict.value}, Indicators: {len(modality_results['text'].indicators)}"
                )
            )

        # ----------------- STEP 3: CORRELATE -----------------
        cross_modal_findings = self.correlator.correlate(modality_results)
        custody_records.append(
            create_custody_record(
                "CROSS_MODAL_CORRELATION_COMPLETED",
                "multimodal_evidence_set",
                "N/A",
                notes=f"Generated {len(cross_modal_findings)} cross-modal findings across {len(modality_results)} modalities."
            )
        )

        # ----------------- STEP 4: REVIEW & CALIBRATE -----------------
        assessment = self.scorer.evaluate(modality_results, cross_modal_findings)

        # ----------------- STEP 5: REPORT & PERSIST -----------------
        report = self.report_generator.build_report(
            case_title=case_title,
            investigator=investigator,
            assessment=assessment,
            modality_results=modality_results,
            cross_modal_findings=cross_modal_findings,
            custody_records=custody_records,
            case_id=active_case_id
        )

        # Persist to PostgreSQL / SQLite database
        self._persist_case_to_database(report, stored_evidence_records)

        return report

    def _persist_case_to_database(
        self, report: ForensicReport, stored_evidence_records: List[Dict[str, Any]]
    ):
        """Persists the case, evidence files, indicators, findings, and chain of custody to database."""
        session = SessionLocal()
        try:
            # Create Case Record
            case_db = CaseRecordDB(
                case_id=report.case_id,
                report_id=report.report_id,
                title=report.case_title,
                investigator=report.investigator,
                overall_verdict=report.assessment.overall_verdict.value,
                manipulation_score=report.assessment.overall_manipulation_score,
                calibrated_confidence=report.assessment.calibrated_confidence,
                status="COMPLETED",
                evidential_summary=report.assessment.evidential_summary
            )
            session.add(case_db)
            session.flush()

            # Store Evidence Files with SHA-256 and MIME Type
            for ev in stored_evidence_records:
                ev_db = EvidenceFileDB(
                    case_id=report.case_id,
                    modality=ev.get("mime_type", "").split("/")[0] if "/" in ev.get("mime_type", "") else "unknown",
                    original_filename=ev["original_filename"],
                    storage_key=ev["storage_key"],
                    sha256_hash=ev["sha256"],
                    mime_type=ev["mime_type"],
                    file_size_bytes=ev["size_bytes"]
                )
                session.add(ev_db)

            # Store Indicators
            for ind in report.all_indicators:
                loc_val_json = json.dumps(ind.evidence_ref.location_value) if ind.evidence_ref else None
                loc_type = ind.evidence_ref.location_type if ind.evidence_ref else None
                ind_db = IndicatorDB(
                    case_id=report.case_id,
                    indicator_id=ind.indicator_id,
                    category=ind.category.value,
                    modality=ind.modality.value,
                    title=ind.title,
                    description=ind.description,
                    technical_details=ind.technical_details,
                    severity=ind.severity.value,
                    suspicion_score=ind.suspicion_score,
                    confidence=ind.confidence,
                    location_type=loc_type,
                    location_value_json=loc_val_json
                )
                session.add(ind_db)

            # Store Cross-Modal Findings
            for cm in report.cross_modal_findings:
                cm_db = CrossModalFindingDB(
                    case_id=report.case_id,
                    finding_id=cm.finding_id,
                    correlation_type=cm.correlation_type,
                    status=cm.status,
                    description=cm.description,
                    details=cm.details,
                    risk_impact=cm.risk_impact,
                    confidence=cm.confidence
                )
                session.add(cm_db)

            # Store Chain of Custody
            for cust in report.chain_of_custody:
                cust_db = ChainOfCustodyDB(
                    case_id=report.case_id,
                    timestamp=cust.timestamp,
                    event=cust.event,
                    performed_by=cust.performed_by,
                    file_name=cust.file_name,
                    sha256=cust.sha256,
                    notes=cust.notes
                )
                session.add(cust_db)

            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()
