from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import string
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=request.email,
        full_name=request.full_name,
        hashed_password=hash_password(request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)


# ── Forgot Password ───────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email address")

    # Generate 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    expires = datetime.utcnow() + timedelta(minutes=15)

    # Save code to database
    user.reset_code = code
    user.reset_code_expires = expires
    db.commit()

    # Send email
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "SecureScan — Password Reset Code"
        msg["From"] = settings.MAIL_FROM
        msg["To"] = user.email

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #0f172a; color: #ffffff; padding: 40px;">
            <div style="max-width: 500px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 40px;">
                <h1 style="color: #3b82f6; margin-bottom: 8px;">SecureScan</h1>
                <p style="color: #94a3b8;">Forensic Document Verification System</p>
                <hr style="border-color: #334155; margin: 24px 0;">
                <h2 style="color: #ffffff;">Password Reset Code</h2>
                <p style="color: #94a3b8;">Hello {user.full_name},</p>
                <p style="color: #94a3b8;">You requested a password reset for your SecureScan account. Use the code below to reset your password:</p>
                <div style="background: #0f172a; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
                    <p style="font-size: 48px; font-weight: bold; letter-spacing: 12px; color: #3b82f6; margin: 0;">{code}</p>
                </div>
                <p style="color: #94a3b8;">This code expires in <strong style="color: #ffffff;">15 minutes</strong>.</p>
                <p style="color: #94a3b8;">If you did not request a password reset, please ignore this email.</p>
                <hr style="border-color: #334155; margin: 24px 0;">
                <p style="color: #475569; font-size: 12px;">University of Bamenda — College of Technology</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, user.email, msg.as_string())

    except Exception as e:
        print(f"Email error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reset email. Please try again.")

    return {"message": "Reset code sent to your email address"}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email address")

    # Check code
    if not user.reset_code or user.reset_code != request.code:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    # Check expiry
    if not user.reset_code_expires or datetime.utcnow() > user.reset_code_expires:
        raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")

    # Update password
    user.hashed_password = hash_password(request.new_password)
    user.reset_code = None
    user.reset_code_expires = None
    db.commit()

    return {"message": "Password reset successfully"}