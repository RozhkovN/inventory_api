# app/schemas/stock_operation.py
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OperationType(str, Enum):
    INCOMING = "INCOMING"
    SALE = "SALE"
    ADJUSTMENT = "ADJUSTMENT"

class StockOperationResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None  # Добавляется в API
    operation_type: str
    quantity_change: int
    old_quantity: Optional[int]
    new_quantity: Optional[int]
    old_purchase_price: Optional[Decimal]
    new_purchase_price: Optional[Decimal]
    old_coefficient: Optional[Decimal]
    new_coefficient: Optional[Decimal]
    sold_price_per_unit: Optional[Decimal]
    reason: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True