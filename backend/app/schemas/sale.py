from pydantic import BaseModel, computed_field
from typing import List, Optional
from decimal import Decimal

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    sold_price_per_unit: Decimal
    coefficient: Decimal = 1.0  # НДС, наличка и т.д. (по дефолту 1.0)

class SaleCreate(BaseModel):
    client_name: str
    items: List[SaleItemCreate]

class SaleStatusUpdate(BaseModel):
    payment_status: str

class SaleItemResponse(BaseModel):
    product_id: int
    product_name: str
    product_sku: Optional[str]
    quantity: int
    sold_price_per_unit: Decimal
    coefficient: Decimal

    @computed_field
    @property
    def final_sell_price(self) -> Decimal:
        """Итоговая цена за единицу товара с учётом коэффициента"""
        return self.sold_price_per_unit * self.coefficient

    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id: int
    client_name: str
    total_sale: Decimal
    total_cost: Decimal
    margin: Decimal
    payment_status: str
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True