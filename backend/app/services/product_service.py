# inventory_api/app/services/product_service.py
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.stock_operation import StockOperation, OperationType

def create_product(db: Session, product_in: ProductCreate):
    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, update_data: ProductUpdate):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None

    old_qty = db_product.quantity
    old_price = db_product.purchase_price
    old_coeff = db_product.coefficient

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(db_product, field, value)

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Логируем операцию
    op = StockOperation(
        product_id=product_id,
        operation_type=OperationType.ADJUSTMENT,
        quantity_change=db_product.quantity - old_qty,
        old_quantity=old_qty,
        new_quantity=db_product.quantity,
        old_purchase_price=old_price,
        new_purchase_price=db_product.purchase_price,
        old_coefficient=old_coeff,
        new_coefficient=db_product.coefficient,
        reason="Ручная корректировка"
    )
    db.add(op)
    db.commit()

    return db_product

def search_products(db: Session, query: str = None):
    q = db.query(Product)
    if query:
        q = q.filter(Product.name.ilike(f"%{query}%"))
    return q.all()