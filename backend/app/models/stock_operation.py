from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, DateTime, func, Enum
from app.database import Base
import enum

class OperationType(str, enum.Enum):
    INCOMING = "INCOMING"
    SALE = "SALE"
    ADJUSTMENT = "ADJUSTMENT"

class StockOperation(Base):
    __tablename__ = "stock_operations"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    operation_type = Column(Enum(OperationType), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    old_quantity = Column(Integer, nullable=True)
    new_quantity = Column(Integer, nullable=True)
    old_purchase_price = Column(Numeric(15, 2), nullable=True)
    new_purchase_price = Column(Numeric(15, 2), nullable=True)
    old_coefficient = Column(Numeric(10, 4), nullable=True)
    new_coefficient = Column(Numeric(10, 4), nullable=True)
    sold_price_per_unit = Column(Numeric(15, 2), nullable=True)
    reason = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)