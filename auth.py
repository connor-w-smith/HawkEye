
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from inventory import user_login_verification, add_user_credentials

router = APIRouter()

class LoginRequest(BaseModel):
    username: EmailStr      # ensures valid email
    password: str

class AddUserRequest(BaseModel):
    username: EmailStr
    password: str
    is_admin: bool

class DeleteUserRequest(BaseModel):
    username: EmailStr

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

#endpoint for user login
@router.post("/login")
def login(data: LoginRequest):
    try:
        permissions = user_login_verification(data.username, data.password)
        return
        {
            "status": "success",
            "permissions": permissions
        }
    except Exception as e:
        #Convert errors to HTTP responses
        raise HTTPException(status_code=401, detail=str(e))

#endpoint to add user
@router.post("/add-user")
def add_user(data: AddUserRequest):
    try:
        #Call function from inventory.py
        return add_user_credentials(data.username, data.password, data.is_admin)
    except Exception as e:
        #Convert errors to HTTP responses
        raise HTTPException(status_code=400, detail=str(e))

#endpoint to delete user
@router.delete("/delete-user")
def delete_user(data: DeleteUserRequest):
    try:
        return delete_user_credentials(data.username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/request-password-reset")
def request_password_reset(data: PasswordResetRequest):
    try:
        password_recovery(data.username)
        return {"status": "ok"}
    except Exception:
        return {"status": "User not found"}

#endpoint to verify and reset password
@router.post("/reset-password")
def user_password_reset(data: PasswordResetRequest):
    try:
        return verify_and_reset_password(data.raw_token, data.new_password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password")
def reset_password(data: PasswordResetConfirm):
    try:
        verify_and_reset_password(
            data.token,
            data.new_password
        )
        return {"status": "success"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
