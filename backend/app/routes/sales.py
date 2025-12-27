# app/routes/sales.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Optional
from app.database import get_db
from app.models.sale import Sale, SaleItem, PaymentStatus
from app.models.product import Product
from app.models.stock_operation import StockOperation, OperationType
from app.schemas.sale import (
    SaleCreate,
    SaleStatusUpdate,
    SaleItemResponse,
    SaleResponse
)

router = APIRouter()


@router.post("/sales", response_model=SaleResponse, summary="Создать продажу")
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    total_sale = Decimal(0)
    total_cost = Decimal(0)
    sale_items_to_create = []

    for item in sale.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(404, f"Товар с id={item.product_id} не найден")
        if product.quantity < item.quantity:
            raise HTTPException(400, f"Недостаточно товара '{product.name}' на складе")

        # Расчёт стоимости с учётом коэффициента
        item_cost = product.purchase_price * item.quantity
        final_price_per_unit = item.sold_price_per_unit * item.coefficient
        item_revenue = final_price_per_unit * item.quantity
        total_cost += item_cost
        total_sale += item_revenue

        # Списываем товар
        product.quantity -= item.quantity
        db.add(product)

        # Создаём SaleItem с коэффициентом
        sale_item = SaleItem(
            product_id=item.product_id,
            quantity=item.quantity,
            sold_price_per_unit=item.sold_price_per_unit,
            coefficient=item.coefficient,
            purchase_price_at_sale=product.purchase_price
        )
        sale_items_to_create.append(sale_item)

        # Логируем списание
        op = StockOperation(
            product_id=item.product_id,
            operation_type=OperationType.SALE,
            quantity_change=-item.quantity,
            old_quantity=product.quantity + item.quantity,
            new_quantity=product.quantity,
            sold_price_per_unit=item.sold_price_per_unit
        )
        db.add(op)

    # Сохраняем продажу
    new_sale = Sale(
        client_name=sale.client_name,
        total_sale=total_sale,
        total_cost=total_cost,
        margin=total_sale - total_cost,
        payment_status=PaymentStatus.UNPAID
    )
    db.add(new_sale)
    db.flush()  # Получаем ID

    # Связываем SaleItem с Sale
    for si in sale_items_to_create:
        si.sale_id = new_sale.id
        db.add(si)

    db.commit()
    db.refresh(new_sale)

    # Формируем ответ с названиями и SKU
    items_response = []
    for si in sale_items_to_create:
        product = db.query(Product).filter(Product.id == si.product_id).first()
        items_response.append(
            SaleItemResponse(
                product_id=si.product_id,
                product_name=product.name if product else "УДАЛЁН",
                product_sku=product.sku if product and product.sku else None,
                quantity=si.quantity,
                sold_price_per_unit=si.sold_price_per_unit,
                coefficient=si.coefficient
            )
        )

    return SaleResponse(
        id=new_sale.id,
        client_name=new_sale.client_name,
        total_sale=new_sale.total_sale,
        total_cost=new_sale.total_cost,
        margin=new_sale.margin,
        payment_status=new_sale.payment_status,
        items=items_response
    )


@router.get("/sales", response_model=List[SaleResponse], summary="Получить все продажи")
def get_all_sales(
    status: Optional[str] = Query(None, enum=["PAID", "UNPAID", "PARTIAL"]),
    db: Session = Depends(get_db)
):
    query = db.query(Sale)
    if status:
        query = query.filter(Sale.payment_status == status)
    sales = query.all()

    sales_response = []
    for sale in sales:
        items = db.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
        items_response = []
        for si in items:
            product = db.query(Product).filter(Product.id == si.product_id).first()
            items_response.append(
                SaleItemResponse(
                    product_id=si.product_id,
                    product_name=product.name if product else "УДАЛЁН",
                    product_sku=product.sku if product and product.sku else None,
                    quantity=si.quantity,
                    sold_price_per_unit=si.sold_price_per_unit,
                    coefficient=si.coefficient
                )
            )
        sales_response.append(
            SaleResponse(
                id=sale.id,
                client_name=sale.client_name,
                total_sale=sale.total_sale,
                total_cost=sale.total_cost,
                margin=sale.margin,
                payment_status=sale.payment_status,
                items=items_response
            )
        )
    return sales_response


@router.put("/sales/{id}/status", summary="Изменить статус оплаты")
def update_sale_status(id: int, update: SaleStatusUpdate, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == id).first()
    if not sale:
        raise HTTPException(404, "Продажа не найдена")
    if update.payment_status not in ["PAID", "UNPAID", "PARTIAL"]:
        raise HTTPException(400, "Недопустимый статус оплаты")
    sale.payment_status = update.payment_status
    db.commit()
    return {"detail": "Статус обновлён"}


@router.delete("/sales/{id}", summary="Удалить продажу и вернуть товары на склад")
def delete_sale(id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == id).first()
    if not sale:
        raise HTTPException(404, "Продажа не найдена")

    items = db.query(SaleItem).filter(SaleItem.sale_id == id).all()
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.quantity += item.quantity
            db.add(product)
            # Лог возврата
            op = StockOperation(
                product_id=item.product_id,
                operation_type=OperationType.ADJUSTMENT,
                quantity_change=item.quantity,
                old_quantity=product.quantity - item.quantity,
                new_quantity=product.quantity,
                reason=f"Отмена продажи #{id}"
            )
            db.add(op)

    db.query(SaleItem).filter(SaleItem.sale_id == id).delete()
    db.delete(sale)
    db.commit()
    return {"detail": "Продажа удалена, остатки восстановлены"}