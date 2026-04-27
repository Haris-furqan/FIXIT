from pydantic import BaseModel
from models import UserRole

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    cnic: str
    role: UserRole