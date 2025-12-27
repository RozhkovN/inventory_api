from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, Enum, ForeignKey
from app.database import Base
import enum

class PaymentStatus(str, enum.Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    PARTIAL = "PARTIAL"

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, nullable=False)
    total_sale = Column(Numeric(15, 2), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    margin = Column(Numeric(15, 2), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)
    created_at = Column(DateTime, default=func.now())

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    sold_price_per_unit = Column(Numeric(15, 2), nullable=False)
    coefficient = Column(Numeric(10, 4), default=1.0, nullable=False)  # НДС, наличка и т.д.
    purchase_price_at_sale = Column(Numeric(15, 2), nullable=False)