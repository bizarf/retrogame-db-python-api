from pydantic import BaseModel, EmailStr
from datetime import datetime


# modal for data returned from me route
class User(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    role: str
    join_date: datetime