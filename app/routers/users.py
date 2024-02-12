from fastapi import APIRouter

router = APIRouter()

@router.get("/users/")
def get_users():
    return {"hello": "hello"}

@router.post("/users/")
def post_users():
    return {"hello": "hello"}