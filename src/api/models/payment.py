from typing import Optional
import datetime
from pydantic import BaseModel

class Payment(BaseModel):
    orderID: int
    transactionAmount: float
    paymentMethod: Optional[str] = None
    transactionDate: Optional[datetime.datetime] = None
    transactionStatus: Optional[str] = None
