from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models.user import User
from app.models.hash_template import HashTemplate
from app.api.auth import get_current_user, get_admin_user
from app.core.security import hash_password

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