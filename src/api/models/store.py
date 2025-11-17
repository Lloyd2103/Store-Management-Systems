from typing import Optional
import datetime
from pydantic import BaseModel

class Store(BaseModel):
    productID: int
    inventoryID: int
    storeDate: Optional[datetime.datetime] = None
    quantityStore: int
    roleStore: Optional[str] = None
