# test_api_full.py
import asyncio
import time
import httpx

BASE_URL = "http://localhost:8700/api"

async def log(msg):
    print("\n✅", msg)
    await asyncio.sleep(1)

async def test_full_workflow():
    async with httpx.AsyncClient(timeout=30.0) as client:

        # === 1. Добавление товаров на склад ===
        await log("1. Добавляем 3 товара на склад")
        products_to_add = [
            {"name": "ТОНЕР-КАРТРИДЖ ЧЕРНЫЙ C60", "sku": "C60-BLK-TN-01", "purchase_price": "2800.00", "coefficient": "1.2", "quantity": 5},
            {"name": "ТОНЕР-КАРТРИДЖ СИНИЙ C60", "sku": "C60-CYN-TN-01", "purchase_price": "3100.00", "coefficient": "1.1", "quantity": 3},
            {"name": "ЧИП НА ДРАМ DC250", "sku": "DC250-DRM-CH-01", "purchase_price": "50.00", "coefficient": "1.0", "quantity": 10}
        ]

        created_ids = []
        for p in products_to_add:
            resp = await client.post(f"{BASE_URL}/products", json=p)
            if resp.status_code == 200:
                data = resp.json()
                created_ids.append(data["id"])
                print(f"  → Добавлен: {data['name']} (id={data['id']}, qty={data['quantity']})")
            else:
                print(f"  ❌ Ошибка добавления: {resp.text}")

        await asyncio.sleep(1)

        # === 2. Обновление товаров ===
        await log("2. Обновляем цену и количество у первых двух товаров")
        updates = [
            {"id": created_ids[0], "quantity": 8, "purchase_price": "2900.00", "coefficient": "1.25"},
            {"id": created_ids[1], "quantity": 7, "purchase_price": "3200.00"}
        ]

        for upd in updates:
            pid = upd.pop("id")
            resp = await client.put(f"{BASE_URL}/products/{pid}", json=upd)
            if resp.status_code == 200:
                data = resp.json()
                print(f"  → Обновлён: {data['name']} → qty={data['quantity']}, цена={data['purchase_price']}, coeff={data['coefficient']}")
            else:
                print(f"  ❌ Ошибка обновления: {resp.text}")

        await asyncio.sleep(1)

        # === 3. Удаление товара (только если qty=0) ===
        await log("3. Пытаемся удалить товар с остатком → должно быть запрещено")
        resp = await client.delete(f"{BASE_URL}/products/{created_ids[2]}")
        print(f"  → Удаление: статус {resp.status_code} – {'запрещено (остаток > 0)' if resp.status_code == 400 else 'успешно'}")

        # Уменьшаем остаток до 0 и удаляем
        await log("   → Устанавливаем количество = 0 и удаляем")
        await client.put(f"{BASE_URL}/products/{created_ids[2]}", json={"quantity": 0})
        resp = await client.delete(f"{BASE_URL}/products/{created_ids[2]}")
        print(f"  → Удаление после обнуления: статус {resp.status_code}")

        await asyncio.sleep(1)

        # === 4. Поиск по части названия ===
        await log("4. Поиск товаров по слову 'ТОНЕР'")
        resp = await client.get(f"{BASE_URL}/products", params={"q": "ТОНЕР"})
        if resp.status_code == 200:
            results = resp.json()
            print(f"  → Найдено {len(results)} товаров:")
            for r in results:
                print(f"    - {r['name']} (sku={r['sku']}, qty={r['quantity']})")
        else:
            print("  ❌ Ошибка поиска")

        await asyncio.sleep(1)

        # === 5. Создание продаж ===
        # === 5. Создание продаж (по 4 товара в каждой) ===
        await log("5. Создаём 2 продажи по 4 позиции каждая (с разными коэффициентами)")
        sales_to_create = [
            {
                "client_name": "Тестовый Клиент 1",
                "items": [
                    {"product_id": created_ids[0], "quantity": 2, "sold_price_per_unit": "3800.00", "coefficient": "1.0"},  # без НДС
                    {"product_id": created_ids[1], "quantity": 1, "sold_price_per_unit": "4000.00", "coefficient": "1.2"},  # наличка
                    {"product_id": created_ids[0], "quantity": 1, "sold_price_per_unit": "3850.00", "coefficient": "1.1"},  # ещё позиция того же товара
                    {"product_id": created_ids[1], "quantity": 2, "sold_price_per_unit": "3950.00", "coefficient": "1.0"}
                ]
            },
            {
                "client_name": "Тестовый Клиент 2",
                "items": [
                    {"product_id": created_ids[0], "quantity": 3, "sold_price_per_unit": "3900.00", "coefficient": "1.2"},
                    {"product_id": created_ids[1], "quantity": 1, "sold_price_per_unit": "4100.00", "coefficient": "1.0"},
                    {"product_id": created_ids[0], "quantity": 1, "sold_price_per_unit": "3880.00", "coefficient": "1.15"},
                    {"product_id": created_ids[1], "quantity": 1, "sold_price_per_unit": "4050.00", "coefficient": "1.0"}
                ]
            }
        ]

        sale_ids = []
        for sale in sales_to_create:
            resp = await client.post(f"{BASE_URL}/sales", json=sale)
            if resp.status_code == 200:
                data = resp.json()
                sale_ids.append(data["id"])
                print(f"  → Продажа #{data['id']} для '{data['client_name']}' на сумму {data['total_sale']}")
                for item in data["items"]:
                    print(f"    → {item['quantity']} шт по {item['sold_price_per_unit']}")
            else:
                print(f"  ❌ Ошибка создания продажи: {resp.text}")

        await asyncio.sleep(1)

        # === 6. Удаление продажи (с возвратом на склад) ===
        await log("6. Удаляем первую продажу → товары должны вернуться на склад")
        resp = await client.delete(f"{BASE_URL}/sales/{sale_ids[0]}")
        print(f"  → Удаление продажи #{sale_ids[0]}: статус {resp.status_code}")

        await asyncio.sleep(1)

        # === 7. Получение всех продаж с фильтрацией по статусу ===
        await log("7. Получаем все продажи")
        resp = await client.get(f"{BASE_URL}/sales")
        if resp.status_code == 200:
            sales = resp.json()
            print(f"  → Всего продаж: {len(sales)}")
            for s in sales:
                print(f"    - Продажа #{s['id']}: клиент='{s['client_name']}', сумма={s['total_sale']}, статус={s['payment_status']}")
        else:
            print("  ❌ Ошибка получения продаж")

        await asyncio.sleep(1)

        # === 8. Изменение статуса оплаты ===
        await log("8. Меняем статус второй продажи на 'PAID'")
        if len(sale_ids) > 1:
            resp = await client.put(f"{BASE_URL}/sales/{sale_ids[1]}/status", json={"payment_status": "PAID"})
            if resp.status_code == 200:
                print(f"  → Статус продажи #{sale_ids[1]} обновлён на PAID")
            else:
                print("  ❌ Ошибка обновления статуса")

        await asyncio.sleep(1)

        # === 9. Финальный вывод склада ===
        await log("9. Текущее состояние склада после всех операций")
        resp = await client.get(f"{BASE_URL}/products/all")
        if resp.status_code == 200:
            products = resp.json()
            print(f"  → Всего товаров на складе: {len(products)}")
            for p in products:
                print(f"    - {p['name']} (sku={p['sku']}) → qty={p['quantity']}, закупка={p['purchase_price']}, итоговая цена={p['final_price']}")
        else:
            print("  ❌ Ошибка получения склада")

        await asyncio.sleep(1)

        # === 10. Получение истории операций ===
        await log("10. Получаем историю операций со складом (последние 7 дней)")
        resp = await client.get(f"{BASE_URL}/stock-history", params={"days": 7})
        if resp.status_code == 200:
            history = resp.json()
            print(f"  → Всего операций: {len(history)}")
            for h in history[:10]:  # Показываем первые 10
                op_type = h['operation_type']
                qty_change = h['quantity_change']
                timestamp = h['timestamp']
                print(f"    - {op_type}: {h['product_name']} ({qty_change:+d}) в {timestamp}")
        else:
            print("  ❌ Ошибка получения истории")

        await log("✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())