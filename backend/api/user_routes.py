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

from fastapi import APIRouter, HTTPException
from ..services.user_services import (
    password_recovery,
    send_recovery_email,
    get_user_credentials_table
)
from ..models.user_models import PasswordResetRequest

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
        send_recovery_email(data.email, raw_token)

        print(f"Password recovery intieated for {data.email}, reset link sent")
        return {"status": "ok", "message": "Password reset token generated"}
    except ValueError as e:
        print(f"Password recovery error: {str(e)}")
        return jsonify({"status":"error", "message": str(e)}), 400
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

#returns table for users page
@router.get("/users")
def get_users():
    #returns the users table with username and isadmin
    rows = get_user_credentials_table()
    # Convert tuples to dicts for JSON
    users = [{"username": r[0], "isadmin": r[1]} for r in rows]
    return users
