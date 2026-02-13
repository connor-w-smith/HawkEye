from pydantic import BaseModel, EmailStr

"""login classes"""

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
    username: str
    token: str

class PasswordUpdateRequest(BaseModel):
    username:str
    old_password: str
    new_password:str