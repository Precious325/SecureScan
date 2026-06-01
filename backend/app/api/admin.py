from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
from app.db.database import get_db
from app.models.user import User
from app.models.hash_template import HashTemplate
from app.api.auth import get_current_user, get_admin_user
from app.core.security import hash_password
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── User Management ───────────────────────────────────────────────────────────

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": str(u.created_at)
        }
        for u in users
    ]


class ResetPasswordRequest(BaseModel):
    new_password: str


@router.post("/users/{user_id}/reset-password")
def admin_reset_password(
    user_id: str,
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    user.hashed_password = hash_password(request.new_password)
    db.commit()
    return {"message": f"Password reset successfully for {user.email}"}


@router.post("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if str(user.id) == str(current_user.id):
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}", "is_active": user.is_active}


# ── Hash Template Management ──────────────────────────────────────────────────

class TemplateRequest(BaseModel):
    institution_name: str
    document_type: str
    document_description: str
    sha256_hash: str


@router.post("/templates")
def add_template(
    request: TemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    existing = db.query(HashTemplate).filter(
        HashTemplate.sha256_hash == request.sha256_hash
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This hash is already registered")
    template = HashTemplate(
        institution_name=request.institution_name,
        document_type=request.document_type,
        document_description=request.document_description,
        sha256_hash=request.sha256_hash,
        added_by=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return {"message": "Template added successfully", "id": str(template.id)}


@router.get("/templates")
def get_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    templates = db.query(HashTemplate).order_by(HashTemplate.added_at.desc()).all()
    return [
        {
            "id": str(t.id),
            "institution_name": t.institution_name,
            "document_type": t.document_type,
            "document_description": t.document_description,
            "sha256_hash": t.sha256_hash,
            "added_at": str(t.added_at)
        }
        for t in templates
    ]


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    template = db.query(HashTemplate).filter(HashTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}


# ── Password Reset Request Management ────────────────────────────────────────

@router.get("/reset-requests")
def get_reset_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    from app.models.reset_request import ResetRequest
    requests = db.query(ResetRequest).filter(
        ResetRequest.status == "pending"
    ).order_by(ResetRequest.requested_at.desc()).all()
    return [
        {
            "id": str(r.id),
            "email": r.email,
            "full_name": r.full_name,
            "status": r.status,
            "requested_at": str(r.requested_at)
        }
        for r in requests
    ]


@router.post("/reset-requests/{request_id}/approve")
def approve_reset_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    from app.models.reset_request import ResetRequest

    reset_req = db.query(ResetRequest).filter(ResetRequest.id == request_id).first()
    if not reset_req:
        raise HTTPException(status_code=404, detail="Request not found")

    code = str(random.randint(100000, 999999))
    expires = datetime.utcnow() + timedelta(minutes=15)

    reset_req.reset_code = code
    reset_req.reset_code_expires = expires
    reset_req.status = "approved"

    user = db.query(User).filter(User.email == reset_req.email).first()
    if user:
        user.reset_code = code
        user.reset_code_expires = expires

    db.commit()

    try:
        msg = MIMEText(
            f"Hello {reset_req.full_name},\n\n"
            f"Your password reset request has been approved.\n\n"
            f"Your reset code is: {code}\n\n"
            f"This code expires in 15 minutes.\n\n"
            f"Go to the SecureScan reset password page and enter this code.\n\n"
            f"SecureScan — University of Bamenda COLTECH"
        )
        msg['Subject'] = 'SecureScan Password Reset Code'
        msg['From'] = settings.MAIL_USERNAME
        msg['To'] = reset_req.email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Email error: {e}")

    return {"message": f"Reset code sent to {reset_req.email}"}


@router.post("/reset-requests/{request_id}/reject")
def reject_reset_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    from app.models.reset_request import ResetRequest

    reset_req = db.query(ResetRequest).filter(ResetRequest.id == request_id).first()
    if not reset_req:
        raise HTTPException(status_code=404, detail="Request not found")

    reset_req.status = "rejected"
    db.commit()
    return {"message": "Request rejected"}


# ── All Scans ─────────────────────────────────────────────────────────────────

@router.get("/scans")
def get_all_scans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    from app.models.scan import Scan
    scans = db.query(Scan).order_by(Scan.upload_timestamp.desc()).all()
    return [
        {
            "scan_id": str(s.id),
            "user_id": str(s.user_id),
            "original_filename": s.original_filename,
            "file_format": s.file_format,
            "risk_score": s.risk_score,
            "risk_verdict": s.risk_verdict,
            "hash_match_status": s.hash_match_status,
            "upload_timestamp": str(s.upload_timestamp),
            "sha256_hash": s.sha256_hash,
        }
        for s in scans
    ]