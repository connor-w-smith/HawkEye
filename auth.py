from fastapi import APIRouter, HTTPException, Request, Header, Query
from pydantic import BaseModel, EmailStr
from inventory import *
from search import *

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
    username: str
    token: str

class PasswordUpdateRequest(BaseModel):
    username:str
    old_password: str
    new_password:str


class FinishedGoodNameRequest(BaseModel):
    finished_good_name: str

class AddFinishedGood(BaseModel):
    finished_good_name: str

class DeleteFinishedGood(BaseModel):
    finished_good_name: str

#endpoint for user login
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

#endpoint to get current user
@router.get("/current-user")
def get_current_user(request: Request):
    try:
        # Get username from Authorization header or cookies
        username = request.headers.get("X-Username")
        if not username:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return {"username": username}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

#endpoint to logout
@router.post("/logout")
def logout(request: Request):
    try:
        return {"status": "success", "message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
@router.post("/user-reset-password")
def user_password_update(data: PasswordUpdateRequest):
    try:
        return update_user_password(data.user_name, data.old_password, data.new_password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
def reset_password(data: PasswordResetConfirm):
    try:
        verify_token_password_reset(
            data.token,
            data.new_password
        )
        return {"status": "success"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")



@router.post("/logout")
def logout(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        delete_session(token)
        return {"status": "logged out"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")



@router.get("/finished-good-name-search")
def finished_good_name_search(finished_good_name: str = Query(...)):

    try:
        finished_good_list = search_finished_by_name(finished_good_name)

        return{
            "status": "success",
            "count": len(finished_good_list),
            "results": finished_good_list
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/finished-good-id-search")
def finished_good_id_search(finished_good_id: str = Query(...)):

    try:
        finished_good_list = search_finished_by_id(finished_good_id)

        return{
            "status": "success",
            "count": len(finished_good_list),
            "results": finished_good_list
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/inventory-id")
def inventory_id_search(finished_good_id: str = Query(...)):

    try:
        finished_good_inventory_list = search_inventory_by_id(finished_good_id)

        if len(finished_good_inventory_list) == 0:
            raise HTTPException(status_code=404, detail=f"No inventory found for ID {finished_good_id}")
        return{
            "status": "success",
            "count": len(finished_good_inventory_list),
            "results": finished_good_inventory_list
        }

    except HTTPException:
        # Re-raise the 404 so FastAPI handles it
        raise

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/inventory-name")
def inventory_name_search(finished_good_name: str = Query(...)):
    try:
        finished_good_inventory_list = search_inventory_by_name(finished_good_name)

        if len(finished_good_inventory_list) == 0:
            raise HTTPException(status_code=404, detail=f"No inventory found for ID {finished_good_name}")

        return {
            "status": "success",
            "count": len(finished_good_inventory_list),
            "results": finished_good_inventory_list
        }

    except HTTPException:
        # Re-raise the 404 so FastAPI handles it
        raise

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/add-finished-good")
def add_finished_good(data: AddFinishedGood):
    try:
        #call function from inventory.py
        return add_finished_good(data.finished_good_name)

    except Exception as e:
        #Convert errors to HTTP responses
        raise HTTPException(status_code=400, detail=str(e))

def delete_finished_good(finished_good_id: str = Query(...)):
    try:
        #call function from inventory.py
        return delete_finished_good(finished_good_id)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
