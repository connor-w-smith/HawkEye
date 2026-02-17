from pydantic import BaseModel, EmailStr

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    username: str
    token: str

class AddUserRequest(BaseModel):
    username: EmailStr
    password: str
    is_admin: bool

class DeleteUserRequest(BaseModel):
    username: EmailStr

class PasswordResetConfirm(BaseModel):
    email: str
    token: str
    new_password: str
