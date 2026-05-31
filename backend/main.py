from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from app.db.database import Base, engine
from app.api import auth, scan, admin
from app.models import user, scan as scan_model
from app.models.reset_request import ResetRequest
import os

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create upload and report directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

security = HTTPBearer()

app = FastAPI(
    title="SecureScan API",
    description="Forensic Document Verification System",
    version="1.0.0"
)

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Register routers
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "SecureScan API is running"}