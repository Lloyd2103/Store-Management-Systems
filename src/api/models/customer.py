from typing import Optional
import datetime
from pydantic import BaseModel

class Customer(BaseModel):
    customerName: str
    phone: str
    email: Optional[str] = None
    address: str
    postalCode: Optional[str] = None

class CustomerDebt(BaseModel):
    customerID: int
    debtAmount: float
    debtDate: Optional[datetime.datetime] = None
    note: Optional[str] = None
