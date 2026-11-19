"""
TruthLens - FastAPI Web Application and Forensic API
Provides REST API endpoints for multimodal evidence ingestion, forensic analysis,
MinIO/S3 object storage, PostgreSQL persistence, and serves the interactive
cyber-forensics dashboard.
"""

import io
import os
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.pipeline import TruthLensPipeline
from core.models import ForensicReport
from reporting.report_generator import ForensicReportGenerator
from samples.sample_cases import get_sample_cases
from database.db import get_db, DB_DIALECT
from database.models import CaseRecordDB, EvidenceFileDB, IndicatorDB, CrossModalFindingDB, ChainOfCustodyDB
from sqlalchemy.orm import Session

app = FastAPI(
    title="TruthLens - Multimodal Digital Forensics & Deepfake Detection",
    description="Multimodal media authenticity, cross-modal correlation, and explainable forensic reporting engine.",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = TruthLensPipeline()
report_generator = ForensicReportGenerator()

# In-memory storage for active session reports
REPORTS_DB: Dict[str, ForensicReport] = {}


@app.get("/api/health")
async def health_check():
    """Returns system status, active database dialect, and storage status."""
    return {
        "status": "online",
        "service": "TruthLens Multimodal Digital Forensics",
        "database_backend": DB_DIALECT,
        "supported_modalities": ["image", "video", "audio", "text"],
        "pipeline_version": "1.0.0"
    }


@app.get("/api/sample-cases")
async def list_sample_cases():
    """Returns metadata for pre-packaged forensic sample cases."""
    cases = get_sample_cases()
    summary = {}
    for key, c in cases.items():
        summary[key] = {
            "title": c["title"],
            "description": c["description"],
            "has_image": c.get("image") is not None,
            "has_video": c.get("video") is not None,
            "has_audio": c.get("audio") is not None,
            "has_text": bool(c.get("text")),
        }
    return summary


@app.post("/api/analyze-sample/{case_key}")
async def analyze_sample_case(case_key: str):
    """Executes full forensic pipeline on a selected pre-configured sample case."""
    cases = get_sample_cases()
    if case_key not in cases:
        raise HTTPException(status_code=404, detail="Sample case not found")

    case_data = cases[case_key]

    report = pipeline.run(
        case_title=case_data["title"],
        investigator="TruthLens Demonstration Examiner",
        image_data=case_data.get("image"),
        image_filename=case_data.get("image_filename", "image.jpg"),
        video_data=case_data.get("video"),
        video_filename=case_data.get("video_filename", "video.mp4"),
        audio_data=case_data.get("audio"),
        audio_filename=case_data.get("audio_filename", "audio.wav"),
        text_data=case_data.get("text"),
        text_filename=case_data.get("text_filename", "context.txt"),
    )

    REPORTS_DB[report.report_id] = report
    return report


@app.post("/api/analyze")
async def analyze_evidence(
    case_title: str = Form("Multimodal Forensic Examination"),
    investigator: str = Form("Forensic Examiner"),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    reference_audio: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    text_file: Optional[UploadFile] = File(None)
):
    """Ingests custom user-provided multimodal evidence files and executes forensic analysis."""
    image_bytes = await image.read() if image else None
    image_name = image.filename if image else "evidence_image.jpg"

    video_bytes = await video.read() if video else None
    video_name = video.filename if video else "evidence_video.mp4"

    audio_bytes = await audio.read() if audio else None
    audio_name = audio.filename if audio else "evidence_audio.wav"

    ref_audio_bytes = await reference_audio.read() if reference_audio else None

    final_text = None
    text_name = "context_notes.txt"
    if text_file:
        raw_text_bytes = await text_file.read()
        final_text = raw_text_bytes.decode("utf-8", errors="ignore")
        text_name = text_file.filename
    elif text_content and text_content.strip():
        final_text = text_content.strip()

    if not any([image_bytes, video_bytes, audio_bytes, final_text]):
        raise HTTPException(status_code=400, detail="At least one modality (image, video, audio, or text) must be provided.")

    report = pipeline.run(
        case_title=case_title,
        investigator=investigator,
        image_data=image_bytes,
        image_filename=image_name,
        video_data=video_bytes,
        video_filename=video_name,
        audio_data=audio_bytes,
        audio_filename=audio_name,
        reference_audio_data=ref_audio_bytes,
        text_data=final_text,
        text_filename=text_name,
    )

    REPORTS_DB[report.report_id] = report
    return report


@app.get("/api/cases")
async def list_cases(db: Session = Depends(get_db)):
    """Lists historical forensic cases from database."""
    try:
        cases = db.query(CaseRecordDB).order_by(CaseRecordDB.created_at.desc()).limit(50).all()
        return [
            {
                "case_id": c.case_id,
                "report_id": c.report_id,
                "title": c.title,
                "investigator": c.investigator,
                "verdict": c.overall_verdict,
                "manipulation_score": c.manipulation_score,
                "calibrated_confidence": c.calibrated_confidence,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "evidence_count": len(c.evidence_files)
            }
            for c in cases
        ]
    except Exception as e:
        return []


@app.get("/api/cases/{case_id}")
async def get_case_details(case_id: str, db: Session = Depends(get_db)):
    """Retrieves detailed case records including SHA-256 and MIME metadata for evidence files."""
    case = db.query(CaseRecordDB).filter(CaseRecordDB.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case ID not found")

    return {
        "case_id": case.case_id,
        "report_id": case.report_id,
        "title": case.title,
        "investigator": case.investigator,
        "verdict": case.overall_verdict,
        "manipulation_score": case.manipulation_score,
        "calibrated_confidence": case.calibrated_confidence,
        "summary": case.evidential_summary,
        "evidence_files": [
            {
                "id": ev.id,
                "modality": ev.modality,
                "filename": ev.original_filename,
                "sha256": ev.sha256_hash,
                "mime_type": ev.mime_type,
                "size_bytes": ev.file_size_bytes,
                "storage_key": ev.storage_key
            }
            for ev in case.evidence_files
        ],
        "indicators": [
            {
                "indicator_id": ind.indicator_id,
                "category": ind.category,
                "modality": ind.modality,
                "title": ind.title,
                "description": ind.description,
                "severity": ind.severity,
                "suspicion_score": ind.suspicion_score,
                "confidence": ind.confidence
            }
            for ind in case.indicators
        ],
        "chain_of_custody": [
            {
                "timestamp": cust.timestamp,
                "event": cust.event,
                "file_name": cust.file_name,
                "sha256": cust.sha256,
                "performed_by": cust.performed_by,
                "notes": cust.notes
            }
            for cust in case.chain_of_custody
        ]
    }


@app.get("/api/reports/{report_id}")
async def get_report_json(report_id: str):
    """Retrieves full structured JSON forensic report."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report ID not found in active session cache")
    return REPORTS_DB[report_id]


@app.get("/api/reports/{report_id}/html", response_class=HTMLResponse)
async def get_report_html(report_id: str):
    """Renders standalone printable HTML forensic dossier."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report ID not found in active session cache")
    report = REPORTS_DB[report_id]
    html_content = report_generator.to_html_dossier(report)
    return HTMLResponse(content=html_content)


@app.get("/api/reports/{report_id}/markdown")
async def get_report_markdown(report_id: str):
    """Returns markdown forensic dossier."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report ID not found in active session cache")
    report = REPORTS_DB[report_id]
    md_content = report_generator.to_markdown(report)
    return Response(content=md_content, media_type="text/markdown")


@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serves the TruthLens Interactive Cybersecurity Forensics Single-Page Application."""
    ui_html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(ui_html_path):
        with open(ui_html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>TruthLens Forensic Backend Online</h1><p>Visit /docs for API documentation.</p>")
