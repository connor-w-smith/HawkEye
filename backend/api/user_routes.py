"""
===========================================
user_routes.py
===========================================
Purpose:
Defines all user-related API endpoints.

This file ONLY contains:
- FastAPI route definitions
- Request validation
- HTTPException handling

Business logic is handled in:
services/user_services.py

Models are defined in:
models/user_models.py
"""

from fastapi import APIRouter, HTTPException, Depends
from flask import jsonify
from fastapi.responses import JSONResponse

from ..models import DeleteUserRequest
from ..services import add_user_credentials
from ..services.user_services import *
from..dependencies.permissions import require_admin
from ..models.user_models import (
    PasswordResetConfirm,
    DeleteUserRequest,
    AddUserRequest,
    PasswordResetRequest
)
from ..models.auth_models import PasswordUpdateRequest
from ..dependencies.permissions import require_admin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


#calls password reset
@router.post("/request-password-reset")
def request_password_reset(data: PasswordResetRequest):
    try:
        #calls function to get raw token from auth_services.py
        raw_token = password_recovery(data.email)

        #uses generated token to call send recovery email
        email_sent = send_recovery_email(data.email, raw_token)

        if not email_sent:
            return {"status": "error", "message": "SMTP server rejected the email"}

        print(f"Password recovery intieated for {data.email}, reset link sent")
        return {"status": "ok", "message": "Password reset token generated"}
    except ValueError as e:
        print(f"Password recovery error: {str(e)}")
        return JSONResponse(status_code=400, content = {"status":"error", "message": str(e)})
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password")
def reset_password_endpoint(data: PasswordResetConfirm):
    try:
        return reset_password_with_token(data.email, data.token, data.new_password)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

#returns table for users page
@router.get("/users")
def get_users(admin=Depends(require_admin)):
    #returns the users table with username and isadmin
    rows = get_user_credentials_table()
    # Convert tuples to dicts for JSON
    users = [{"username": r[0], "isadmin": r[1]} for r in rows]
    return users

#endpoint to add user
@router.post("/add-user")
def add_user(data: AddUserRequest, admin=Depends(require_admin)):
    try:
        #Call function from inventory.py
        return add_user_credentials(data.username, data.password, data.is_admin)
    except Exception as e:
        #Convert errors to HTTP responses
        raise HTTPException(status_code=400, detail=str(e))

#delete user updated endpoint
@router.delete("/delete-user/{username}")
def delete_user(username: str, admin=Depends(require_admin)):
    try:
        return delete_user_credentials(username)
    except Exception as e:
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