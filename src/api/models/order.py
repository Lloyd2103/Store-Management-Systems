from typing import Optional, List
import datetime
from pydantic import BaseModel

class Order(BaseModel):
    orderDate: Optional[datetime.datetime] = None
    totalAmount: Optional[float] = 0
    orderStatus: Optional[str] = "Pending"
    paymentDate: Optional[str] = None
    paymentStatus: Optional[str] = "Unpaid"
    pickupMethod: Optional[str] = "Ship"
    shippedDate: Optional[str] = None
    shippedStatus: Optional[str] = "In Process"
    customerID: Optional[int] = None
    staffID: Optional[int] = None

class OrderCheckoutModel(BaseModel):
    customerID: int
    staffID: Optional[int] = None
    paymentMethod: str
    products: List[dict]  # [{productID, quantity, priceEach}]
    pickupMethod: str
    orderStatus: str
    paymentStatus: str
    shippedStatus: str
    shippedDate: Optional[str] = None
