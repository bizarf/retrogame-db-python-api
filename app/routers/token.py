from fastapi import APIRouter, HTTPException
from app.utils.auth_utils import (
    create_access_token,
    verify_refresh_token,
    update_refresh_token,
)

router = APIRouter()


@router.post("/token/refresh")
async def refresh_access_token(refresh_token: str):
    try:
        # Verify the refresh token
        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Generate a new access token and re-encode the refresh token
        new_access_token = create_access_token({"sub": user_id})
        updated_refresh_token = update_refresh_token(refresh_token)

        # Return the new access token
        return {
            "success": True,
            "access_token": new_access_token,
            "refresh_token": updated_refresh_token,
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to refresh access token")
