@echo off
title TruthLens - Multimodal Digital Forensics Server
echo =====================================================================
echo  TruthLens - Multimodal Digital Forensics & Deepfake Detection Engine
echo =====================================================================
echo.
echo Starting FastAPI Uvicorn Server on port 8000...
echo Web Dashboard: http://127.0.0.1:8000/
echo Swagger REST API Docs: http://127.0.0.1:8000/docs
echo.
python -m uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
pause
