from typing import Optional
import datetime
from pydantic import BaseModel

class Supply(BaseModel):
    productID: int
    vendorID: int
    supplyDate: Optional[datetime.datetime] = None
    quantitySupplier: int
    handledBy: Optional[str] = None
