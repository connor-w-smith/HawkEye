from pydantic import BaseModel, EmailStr

class PasswordResetRequest(BaseModel):
    email: EmailStr

class AddUserRequest(BaseModel):
    username: EmailStr
    password: str
    is_admin: bool

class DeleteUserRequest(BaseModel):
    username: EmailStr
