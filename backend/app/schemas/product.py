from pydantic import BaseModel, computed_field
from typing import Optional
from decimal import Decimal

class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    purchase_price: Decimal
    coefficient: Decimal = 1.0
    quantity: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    purchase_price: Optional[Decimal] = None
    coefficient: Optional[Decimal] = None
    quantity: Optional[int] = None

class ProductResponse(ProductBase):
    id: int

    @computed_field
    @property
    def final_price(self) -> Decimal:
        """Итоговая цена с учётом коэффициента (для отображения на складе)"""
        return self.purchase_price * self.coefficient

    class Config:
        from_attributes = True