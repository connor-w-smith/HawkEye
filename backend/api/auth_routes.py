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

from fastapi import APIRouter, HTTPException, Header, Depends

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
from ..dependencies.permissions import get_current_user

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


# Endpoint for logout
@router.post("/logout")
def logout(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        delete_session(token)
        return {"status": "logged out"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")


@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "username": user["username"],
        "isadmin": user["isadmin"],
        "canviewtables": user["canviewtables"],
        "canedittables": user["canedittables"]
    }
