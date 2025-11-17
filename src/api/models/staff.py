from typing import Optional
from pydantic import BaseModel

class Staff(BaseModel):
    staffName: str
    position: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    managerID: Optional[int] = None
    salary: Optional[float] = None
