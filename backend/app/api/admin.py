from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.hash_template import HashTemplate
from app.api.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/admin", tags=["Admin"])

class TemplateCreate(BaseModel):
    institution_name: str
    document_type: str
    document_description: Optional[str] = None
    sha256_hash: str

@router.post("/templates")
def add_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(HashTemplate).filter(
        HashTemplate.sha256_hash == template.sha256_hash
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This hash already exists in the database"
        )

    new_template = HashTemplate(
        institution_name=template.institution_name,
        document_type=template.document_type,
        document_description=template.document_description,
        sha256_hash=template.sha256_hash,
        added_by=current_user.id
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return {
        "message": "Template added successfully",
        "id": str(new_template.id),
        "institution": new_template.institution_name,
        "document_type": new_template.document_type,
        "sha256_hash": new_template.sha256_hash
    }

@router.get("/templates")
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    templates = db.query(HashTemplate).all()
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
    current_user: User = Depends(get_current_user)
):
    template = db.query(HashTemplate).filter(
        HashTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()

    return {"message": "Template deleted successfully"}