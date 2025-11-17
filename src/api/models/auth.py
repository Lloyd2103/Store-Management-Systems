from typing import Optional
from pydantic import BaseModel

class RegisterModel(BaseModel):
    customerName: str
    phone: str
    password: str
    address: str
    postalCode: Optional[str] = None
    email: Optional[str] = None
    customerType: Optional[str] = "Individual"
    loyalPoint: Optional[int] = 0
    loyalLevel: Optional[str] = "New"

class LoginModel(BaseModel):
    identifier: str
    password: str

class RegisterStaffModel(BaseModel):
    staffName: str
    position: Optional[str] = None
    phone: str
    password: str
    email: Optional[str] = None
    address: Optional[str] = None
    managerID: Optional[int] = None
    salary: Optional[float] = None
