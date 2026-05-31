import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.database import Base

class ResetRequest(Base):
    __tablename__ = "reset_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected
    reset_code = Column(String, nullable=True)
    reset_code_expires = Column(DateTime, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)