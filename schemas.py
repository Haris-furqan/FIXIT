from pydantic import BaseModel
from models import UserRole
from typing import Optional
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    cnic: str
    role: UserRole
    profession: Optional[str] = None