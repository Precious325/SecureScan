from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer)
    file_format = Column(String)
    sha256_hash = Column(String)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata_result = Column(JSONB)
    ela_score = Column(Float)
    ela_heatmap_path = Column(String)
    hash_match_status = Column(String)
    risk_score = Column(Integer)
    risk_verdict = Column(String)
    report_path = Column(String)