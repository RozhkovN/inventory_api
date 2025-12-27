from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Optional
from app.database import get_db
from app.models.product import Product
from app.models.stock_operation import StockOperation, OperationType
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.stock_operation import StockOperationResponse

router = APIRouter()

@router.get("/products", response_model=list[ProductResponse], summary="Частичный поиск по названию")
def search_products(q: str = Query(None, min_length=1), db: Session = Depends(get_db)):
    query = db.query(Product)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    return query.all()

@router.get("/products/all", response_model=list[ProductResponse], summary="Все товары")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.post("/products", response_model=ProductResponse, summary="Добавить товар")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    op = StockOperation(
        product_id=db_product.id,
        operation_type=OperationType.INCOMING,
        quantity_change=product.quantity,
        old_quantity=0,
        new_quantity=product.quantity,
        old_purchase_price=Decimal(0),
        new_purchase_price=product.purchase_price,
        old_coefficient=Decimal(1),
        new_coefficient=product.coefficient,
        reason="Ручной приход"
    )
    db.add(op)
    db.commit()
    return db_product

@router.put("/products/{id}", response_model=ProductResponse, summary="Обновить товар")
def update_product(id: int, update: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(404, "Товар не найден")

    old_qty = db_product.quantity
    old_price = db_product.purchase_price
    old_coeff = db_product.coefficient

    for field, value in update.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)

    op = StockOperation(
        product_id=id,
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

@router.delete("/products/{id}", summary="Удалить товар")
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(404, "Товар не найден")
    
    # Сначала удаляем все связанные записи в stock_operations
    db.query(StockOperation).filter(StockOperation.product_id == id).delete()
    
    # Затем удаляем сам товар
    db.delete(product)
    db.commit()
    return {"detail": "Товар и его история удалены"}


@router.get("/stock-history", response_model=List[StockOperationResponse], summary="История операций со складом")
def get_stock_history(
    product_id: Optional[int] = Query(None, description="ID товара для фильтрации"),
    operation_type: Optional[str] = Query(None, enum=["INCOMING", "SALE", "ADJUSTMENT"]),
    days: Optional[int] = Query(None, description="История за последние N дней"),
    db: Session = Depends(get_db)
):
    """
    Получить историю операций со складом с опциональной фильтрацией
    
    - **product_id**: Фильтр по товару
    - **operation_type**: Тип операции (INCOMING, SALE, ADJUSTMENT)
    - **days**: История за последние N дней (если не указано - вся история)
    """
    query = db.query(StockOperation)
    
    if product_id:
        query = query.filter(StockOperation.product_id == product_id)
    
    if operation_type:
        query = query.filter(StockOperation.operation_type == operation_type)
    
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(StockOperation.timestamp >= start_date)
    
    operations = query.order_by(StockOperation.timestamp.desc()).all()
    
    # Добавляем названия товаров
    result = []
    for op in operations:
        product = db.query(Product).filter(Product.id == op.product_id).first()
        response = StockOperationResponse.model_validate(op)
        response.product_name = product.name if product else "УДАЛЁН"
        result.append(response)
    
    return result