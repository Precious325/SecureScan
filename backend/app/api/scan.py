import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.scan import Scan
from app.api.auth import get_current_user
from app.models.user import User
from app.forensics.metadata_engine import analyze_metadata
from app.forensics.ela_engine import perform_ela, perform_ela_on_pdf
from app.forensics.hash_engine import verify_hash
from app.forensics.risk_scorer import compute_risk_score
from app.core.config import settings

router = APIRouter(prefix="/scan", tags=["Scan"])

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


@router.post("/upload")
def upload_and_scan(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="File type not supported. Allowed: PDF, JPG, PNG"
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    temp_filename = f"{uuid.uuid4().hex}{file_ext}"
    temp_path = os.path.join(settings.UPLOAD_DIR, temp_filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(temp_path)

    try:
        metadata_result = analyze_metadata(temp_path, file_ext)

        if file_ext == ".pdf":
            ela_result = perform_ela_on_pdf(temp_path, settings.REPORTS_DIR)
        else:
            ela_result = perform_ela(temp_path, settings.REPORTS_DIR)

        hash_result = verify_hash(temp_path, db)
        risk = compute_risk_score(metadata_result, ela_result, hash_result)

        scan = Scan(
            user_id=current_user.id,
            original_filename=file.filename,
            file_size=file_size,
            file_format=file_ext.replace(".", "").upper(),
            sha256_hash=hash_result.get("sha256_hash"),
            metadata_result=metadata_result,
            ela_score=ela_result.get("ela_score"),
            ela_heatmap_path=ela_result.get("heatmap_path"),
            hash_match_status=hash_result.get("match_status"),
            risk_score=risk["risk_score"],
            risk_verdict=risk["risk_verdict"]
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        return {
            "scan_id": str(scan.id),
            "filename": file.filename,
            "file_format": scan.file_format,
            "file_size_kb": round(file_size / 1024, 2),
            "sha256_hash": hash_result.get("sha256_hash"),
            "layer1_metadata": metadata_result,
            "layer2_ela": ela_result,
            "layer3_hash": hash_result,
            "risk_score": risk["risk_score"],
            "risk_verdict": risk["risk_verdict"],
            "recommendation": risk["recommendation"],
            "color": risk["color"]
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_scan_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scans = db.query(Scan).filter(
        Scan.user_id == current_user.id
    ).order_by(Scan.upload_timestamp.desc()).all()

    return [
        {
            "scan_id": str(s.id),
            "filename": s.original_filename,
            "file_format": s.file_format,
            "risk_score": s.risk_score,
            "risk_verdict": s.risk_verdict,
            "upload_timestamp": str(s.upload_timestamp)
        }
        for s in scans
    ]


@router.get("/{scan_id}/result")
def get_scan_result(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "scan_id": str(scan.id),
        "filename": scan.original_filename,
        "file_format": scan.file_format,
        "file_size_kb": round(scan.file_size / 1024, 2) if scan.file_size else None,
        "sha256_hash": scan.sha256_hash,
        "layer1_metadata": scan.metadata_result,
        "ela_score": scan.ela_score,
        "hash_match_status": scan.hash_match_status,
        "risk_score": scan.risk_score,
        "risk_verdict": scan.risk_verdict,
        "upload_timestamp": str(scan.upload_timestamp)
    }


@router.get("/{scan_id}/report")
def download_report(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.forensics.report_generator import generate_report

    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan_data = {
        "scan_id": str(scan.id),
        "filename": scan.original_filename,
        "file_format": scan.file_format,
        "file_size_kb": round(scan.file_size / 1024, 2) if scan.file_size else 0,
        "sha256_hash": scan.sha256_hash,
        "layer1_metadata": scan.metadata_result,
        "layer2_ela": {
            "ela_score": scan.ela_score,
            "suspicion_flag": scan.ela_score > 0.15 if scan.ela_score else False,
            "interpretation": ""
        },
        "layer3_hash": {
            "match_status": scan.hash_match_status,
            "matched_institution": None,
            "interpretation": ""
        },
        "risk_score": scan.risk_score,
        "risk_verdict": scan.risk_verdict,
        "recommendation": ""
    }

    report_path = generate_report(scan_data)

    return FileResponse(
        path=report_path,
        filename=f"SecureScan_Report_{scan_id[:8]}.pdf",
        media_type="application/pdf"
    )