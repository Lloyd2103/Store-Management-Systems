from typing import Optional
from pydantic import BaseModel

class Vendor(BaseModel):
    vendorName: str
    contactName: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
