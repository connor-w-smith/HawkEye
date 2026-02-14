"""
===========================================
auth_routes.py
===========================================
Purpose:
Defines all authentication-related API endpoints.

This file ONLY contains:
- FastAPI route definitions
- Request validation
- HTTPException handling

Business logic is handled in:
services/auth_service.py

Models are defined in:
models/auth_models.py
"""

from fastapi import APIRouter, HTTPException, Header

from ..models.auth_models import (
    LoginRequest,
    PasswordResetRequest,
    PasswordUpdateRequest,
    PasswordResetConfirm,
)

from ..services.auth_services import (
    user_login_verification,
    create_session,
    validate_session,
    delete_session,

)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# Endpoint for user login
@router.post("/login")
def login(data: LoginRequest):
    try:
        result = user_login_verification(data.username, data.password)
        return {
            "status": "success",
            "session_token": result["token"]
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Endpoint to request password reset
@router.post("/request-password-reset")
def request_password_reset(data: PasswordResetRequest):
    try:
        result = password_recovery_email(data.email)
        print(f"Password recovery result: {result}")
        return {
            "status": "ok",
            "message": "Password reset token generated"
        }
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint to update password (logged-in user)
@router.post("/user-reset-password")
def user_password_update(data: PasswordUpdateRequest):
    try:
        return update_user_password(
            data.username,
            data.old_password,
            data.new_password
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint to reset password using token
@router.post("/reset-password")
def reset_password_endpoint(data: PasswordResetConfirm):
    try:
        return reset_password_with_token(
            data.email,
            data.token,
            data.new_password
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )


# Endpoint for logout
@router.post("/logout")
def logout(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        delete_session(token)
        return {"status": "logged out"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")
