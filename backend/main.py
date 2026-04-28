from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.api import auth, scan, admin
import os

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create upload and report directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

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

# Mount static files for heatmap images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register routers
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "SecureScan API is running"}