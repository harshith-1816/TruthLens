# TruthLens – Multimodal Digital Forensics & Deepfake Detection System

> **Domain:** Digital Forensics & Cybersecurity  
> **Challenge Area:** Multimodal Media Authenticity Analysis  
> **Expected Outcome:** Explainable Forensic Report with Calibrated Certainty  
> **Tech Stack:** Next.js Frontend • FastAPI Backend • PostgreSQL Database • MinIO / S3 Object Storage

---

## 01 | Executive Overview

Modern editing tools and generative AI models can produce highly realistic manipulated images, AI-generated videos, cloned voices, and coordinated misleading text. Traditional single-modality detectors fail when evidence spans multiple formats or when multiple subtle inconsistencies appear together.

**TruthLens** is an end-to-end digital forensics platform that examines media systematically, compares signals across formats, calculates calibrated confidence levels with honest uncertainty, preserves cryptographic evidence context (SHA-256 hashes, MIME types, chain of custody), and generates an explainable forensic report for human review.

---

## 02 | Architectural Architecture & Tech Stack

```
   ┌─────────────────────────────────────────────────────────────┐
   │                    Next.js 14 Web UI                        │
   │  (Interactive Scrubber, ELA/FFT Overlays, Spectrogram,     │
   │   Cross-Modal Matrix, Chain of Custody Table, PDF/MD Export)│
   └──────────────────────────────┬──────────────────────────────┘
                                  │ REST API / CORS
   ┌──────────────────────────────▼──────────────────────────────┐
   │                     FastAPI Backend                         │
   │      (Multimodal Ingestion & Forensic Pipeline Engine)      │
   └───────────────┬──────────────────────────────┬──────────────┘
                   │                              │
   ┌───────────────▼──────────────┐┌──────────────▼──────────────┐
   │    PostgreSQL (SQLAlchemy)   ││      MinIO / S3 Storage     │
   │  - Case Records              ││  - Immutable Vault          │
   │  - Evidence File Registry    ││  - SHA-256 Verification     │
   │  - Flagged Indicators        ││  - MIME-Type Tagging        │
   │  - Cross-Modal Correlations  ││  - S3 Storage Keys          │
   │  - Chain of Custody Audit Log││  - Local Vault Fallback     │
   └──────────────────────────────┘└──────────────────────────────┘
```

---

## 03 | Core Capabilities & Verification Steps

### 1. Image Authenticity Analysis
- **Metadata and File Forensics:** Checks EXIF metadata, camera make/model, exposure settings, software tags (`Adobe Photoshop`, `Midjourney`, `Stable Diffusion`), GPS coordinates, timestamps, and flags stripped metadata (reducing provenance certainty).
- **Pixel & Noise Analysis:** Computes local Laplacian sensor noise variance across spatial tiles and standard scores (Z-scores) to detect spliced patches. Flags unnatural over-smoothing characteristic of AI skin generation.
- **Lighting and Shadow Consistency:** Evaluates luminance directional gradient vectors across image quadrants to detect conflicting illumination sources and chromatic color temperature divergence.
- **Edge and Blending Analysis:** Analyzes boundary gradient transitions and feathering around central subjects to detect alpha mask seam artifacts.
- **Frequency-Domain Analysis:** Performs Error Level Analysis (ELA) for re-compression disparities and 2D FFT magnitude spectrum analysis to reveal GAN / Latent Diffusion periodic checkerboard artifacts.
- **AI Synthetic Feature Attribution:** Computes multivariate synthesis attribution likelihood and outputs an attribution heatmap highlighting suspicious facial/object bounding boxes.

### 2. Video Forensics
- **Frame Extraction & Temporal Consistency:** Decomposes video into frames and computes inter-frame Mean Squared Error (MSE) to detect temporal flicker and frame dropping.
- **Facial Landmark & Jawline Stability:** Tracks mouth, eyes, and jawline edge contours across consecutive frames to flag landmark flicker (e.g. jawline displacement at `00:12–00:14`).
- **Biological-Signal Checks:** Monitors spontaneous physiological blinking frequency and gaze continuity; flags unnatural fixed stares (>6s without blinks).
- **Optical Flow Decoupling:** Measures differential pixel motion between the central subject and peripheral scene to detect decoupled reenactment overlays.
- **Container Structure & Tool Signatures:** Inspects ISO media atoms (`ftyp`, `moov`, `mvhd`) for deepfake framework tags (`DeepFaceLab`, `FaceSwap`, `Roop`, `SadTalker`, `Wav2Lip`).

### 3. Audio & Voice Analysis
- **Spectral Analysis:** Computes spectral centroid, spectral rolloff, and detects neural vocoder brickwall filter cutoffs (>8kHz zero-energy cliff typical of HiFi-GAN, FastSpeech, ElevenLabs).
- **Temporal & Dynamics Analysis:** Analyzes speech cadence, pause distribution, and flags dead digital silence (absolute 0 amplitude gaps between concatenated speech chunks).
- **Phonetic and Prosodic Analysis:** Tracks fundamental frequency (F0) pitch contours and measures pitch micro-tremors (jitter); flags robotic pitch monotony (<0.5 Hz jitter).
- **Audio Editing & Splicing Detection:** Identifies abrupt ambient noise floor shifts and room acoustic discontinuities (e.g. background noise jumping at `00:03–00:04`).
- **Speaker Voiceprint Comparison:** Extracts 16-band spectral feature embeddings and computes cosine similarity against a known reference sample of the claimed speaker.

### 4. Text & Context Forensics
- **Claim Extraction:** Extracts dates, years, locations, and proper nouns from captions, transcripts, and social dispatches.
- **Stylometric Burstiness & Uniformity:** Measures sentence length coefficient of variation (CV) and Type-Token Ratio (TTR) to detect mathematical LLM uniformity (CV < 0.22 vs human > 0.45).
- **LLM Hallmarking:** Identifies concentrations of canonical LLM boilerplate ("delve into", "testament to", "it is crucial to remember").
- **Disinformation Urgency Hooks:** Flags viral psychological pressure patterns ("share before they delete this", "mainstream media won't show you this").
- **Cross-Modal Contradictions:** Flags explicit factual conflicts between context and media (e.g., text claiming broad daylight sunny morning in Mumbai while visual evidence shows dark nighttime indoor illumination).

### 5. Cross-Modal Correlation & Calibrated Scoring
- **Evidential Fusion:** Merges signals across Image, Video, Audio, and Text into calibrated confidence scores (0-100).
- **Correlation Classifications:** Categorizes findings into `CORROBORATING_MANIPULATION`, `CORROBORATING_AUTHENTIC`, and `CONTRADICTION`.
- **Honest Uncertainty & Alternative Explanations:** Explains known limitations (e.g., lossy compression noise vs malicious tampering) and outlines alternative benign hypotheses.
- **Human Examiner Checklist:** Generates an actionable verification checklist for qualified forensic specialists.
- **Cryptographic Chain of Custody:** Tracks every file ingestion and forensic step with SHA-256 hashes, timestamps, and examiner credentials.

---

## 04 | Getting Started & Running TruthLens

### Prerequisites
- Python 3.10+ (tested with Python 3.14)
- (Optional) Docker for PostgreSQL and MinIO

### 1. Quick Start (Automatic SQLite & Local Vault Fallback)
TruthLens runs out-of-the-box with zero configuration:
```powershell
# Navigate to project directory
cd C:\Users\DELL\.gemini\antigravity\scratch\truthlens

# Run backend API and Interactive Cyber-Forensics Web Dashboard
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser at:
- **Interactive Cyber-Forensics Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger REST API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Optional: Running PostgreSQL & MinIO with Docker
```powershell
docker compose up -d
```
Environment variables:
- `DATABASE_URL`: `postgresql://postgres:postgrespassword@localhost:5432/truthlens_db`
- `MINIO_ENDPOINT`: `localhost:9000`
- `MINIO_ACCESS_KEY`: `minioadmin`
- `MINIO_SECRET_KEY`: `minioadminpassword`

### 3. Running Next.js Frontend (when Node.js is installed)
```powershell
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) for the Next.js frontend, which proxies requests to the FastAPI backend at port 8000.

---

## 05 | Automated Test Suite

TruthLens includes a full suite of automated unit and end-to-end integration tests:
```powershell
python -m pytest tests/ -v
```
All 13 test suites pass:
- `test_api_health` - Verifies online status and modality registries.
- `test_api_sample_cases` - Tests sample case discovery.
- `test_api_analyze_sample_case` - Tests end-to-end sample analysis.
- `test_api_list_cases` - Tests database case history.
- `test_ui_root` - Verifies web dashboard delivery.
- `test_synthetic_cloned_audio_detection` - Tests vocoder cutoffs and pitch monotony.
- `test_authentic_audio_detection` - Tests wideband acoustics and natural jitter.
- `test_synthetic_image_detection` - Tests FFT periodic peaks and AI prompt tags.
- `test_spliced_image_detection` - Tests localized ELA and noise Z-scores.
- `test_authentic_image_detection` - Tests camera EXIF and natural sensor noise.
- `test_llm_disinfo_text_detection` - Tests burstiness CV and disinfo markers.
- `test_end_to_end_pipeline_and_storage` - Tests full 5-step pipeline and SHA-256 custody.
- `test_synthetic_video_jitter_detection` - Tests temporal inter-frame MSE spikes.

---

## 06 | Evidence Traceability & Report Formats

Every analysis produces an evidentiary dossier accessible via:
- **Interactive Web Interface:** Real-time visual spectrum scrubbing, bounding box previews, and checklist.
- **Printable HTML Forensic Dossier:** `GET /api/reports/{report_id}/html`
- **Markdown Dossier:** `GET /api/reports/{report_id}/markdown`
- **Machine-Readable JSON:** `GET /api/reports/{report_id}`
