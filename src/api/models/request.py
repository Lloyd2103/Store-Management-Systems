from typing import Optional
from pydantic import BaseModel

class Request(BaseModel):
    orderID: int
    productID: int
    quantityOrdered: int
    discount: Optional[float] = 0
    note: str
