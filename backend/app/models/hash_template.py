from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class HashTemplate(Base):
    __tablename__ = "hash_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_name = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    document_description = Column(String)
    sha256_hash = Column(String, unique=True, nullable=False)
    added_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    added_at = Column(DateTime(timezone=True), server_default=func.now())