from typing import Optional
import datetime
from pydantic import BaseModel

class Inventory(BaseModel):
    inventoryID: int
    warehouse: str
    maxStockLevel: int
    stockQuantity: int
    unitCost: float
    lastedUpdate: Optional[datetime.datetime] = None
    inventoryNote: Optional[str] = None
    inventoryStatus: Optional[str] = "Active"

class InventoryImport(BaseModel):
    productID: int
    inventoryID: int
    quantity: int
    importDate: Optional[datetime.datetime] = None
    unitCost: float
    note: Optional[str] = None

class InventoryExport(BaseModel):
    productID: int
    inventoryID: int
    quantity: int
    exportDate: Optional[datetime.datetime] = None
    reason: Optional[str] = None
    note: Optional[str] = None

class Stocktaking(BaseModel):
    inventoryID: int
    productID: int
    actualQuantity: int
    stocktakingDate: Optional[datetime.datetime] = None
    note: Optional[str] = None
