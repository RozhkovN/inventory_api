from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, nullable=True, index=True)
    purchase_price = Column(Numeric(15, 2), nullable=False)
    coefficient = Column(Numeric(10, 4), default=1.0, nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())