from typing import Optional
from pydantic import BaseModel

class Product(BaseModel):
    productName: str
    priceEach: float
    productLine: str
    productScale: str
    productBrand: str
    productDiscription: str
    warrantyPeriod: int
    MSRP: float

class Category(BaseModel):
    categoryName: str
    description: Optional[str] = None
