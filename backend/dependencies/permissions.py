from fastapi import Header, HTTPException, Depends
from ..services.auth_services import validate_session


# ---------------------------------------------------
# Base Authentication Dependency
# ---------------------------------------------------

def get_current_user(authorization: str = Header(...)):
    """
    Extracts Bearer token from header
    Validates session
    Returns user info + permissions
    """
    try:
        token = authorization.replace("Bearer ", "")
        return validate_session(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session")


# ---------------------------------------------------
# Admin Permission
# ---------------------------------------------------

def require_admin(user=Depends(get_current_user)):
    if not user["isadmin"]:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


# ---------------------------------------------------
# View Tables Permission
# ---------------------------------------------------

def require_view_permission(user=Depends(get_current_user)):
    if not user["canviewtables"] and not user["isadmin"]:
        raise HTTPException(status_code=403, detail="View permission required")
    return user


# ---------------------------------------------------
# Edit Tables Permission
# ---------------------------------------------------

def require_edit_permission(user=Depends(get_current_user)):
    if not user["canedittables"] and not user["isadmin"]:
        raise HTTPException(status_code=403, detail="Edit permission required")
    return user
