#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными.
Создаёт товары и продажи для демонстрации функционала.

Использование:
    python populate_db.py
"""

import requests
import json
import time
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Конфигурация
API_BASE_URL = "http://localhost:8700/api"
DELAY = 0.2  # Задержка между запросами (сек)

# Цвета для консоли
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_status(message, status="INFO"):
    """Вывести статус-сообщение"""
    colors = {
        "SUCCESS": Colors.GREEN,
        "ERROR": Colors.RED,
        "INFO": Colors.CYAN,
        "WARNING": Colors.YELLOW
    }
    color = colors.get(status, Colors.CYAN)
    print(f"{color}[{status}]{Colors.ENDC} {message}")

def check_api_connection():
    """Проверить доступность API"""
    try:
        response = requests.get(f"{API_BASE_URL}/products/all", timeout=5)
        if response.status_code == 200:
            print_status("✅ API доступен", "SUCCESS")
            return True
    except Exception as e:
        print_status(f"❌ API недоступен: {e}", "ERROR")
        print_status("Убедитесь что запущен: docker compose up -d", "WARNING")
        return False

def create_products():
    """Создать товары"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}📦 СОЗДАНИЕ ТОВАРОВ{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    products_data = [
        # Принтеры
        {
            "name": "XEROX Workcentre 5335",
            "sku": "XW-5335",
            "purchase_price": "85000.00",
            "coefficient": "1.0",
            "quantity": 3,
            "category": "Принтеры"
        },
        {
            "name": "XEROX Workcentre 5230",
            "sku": "XW-5230",
            "purchase_price": "72000.00",
            "coefficient": "0.95",  # скидка 5%
            "quantity": 5,
            "category": "Принтеры"
        },
        
        # Картриджи чёрные
        {
            "name": "КАРТРИДЖ ЧЁРНЫЙ 60K",
            "sku": "C60-BLK",
            "purchase_price": "3000.00",
            "coefficient": "0.9",   # скидка 10%
            "quantity": 15,
            "category": "Картриджи"
        },
        {
            "name": "КАРТРИДЖ ЧЁРНЫЙ 100K",
            "sku": "C100-BLK",
            "purchase_price": "4500.00",
            "coefficient": "0.88",  # скидка 12%
            "quantity": 10,
            "category": "Картриджи"
        },
        {
            "name": "КАРТРИДЖ ЧЁРНЫЙ ОРИГИНАЛЬНЫЙ",
            "sku": "ORIG-BLK",
            "purchase_price": "5200.00",
            "coefficient": "1.0",
            "quantity": 8,
            "category": "Картриджи"
        },
        
        # Картриджи цветные
        {
            "name": "КАРТРИДЖ СИНИЙ C75",
            "sku": "C75-CYN",
            "purchase_price": "3100.00",
            "coefficient": "0.9",
            "quantity": 12,
            "category": "Картриджи"
        },
        {
            "name": "КАРТРИДЖ ЖЁЛТЫЙ C75",
            "sku": "C75-YEL",
            "purchase_price": "3100.00",
            "coefficient": "0.9",
            "quantity": 12,
            "category": "Картриджи"
        },
        {
            "name": "КАРТРИДЖ РОЗОВЫЙ C75",
            "sku": "C75-MAG",
            "purchase_price": "3100.00",
            "coefficient": "0.9",
            "quantity": 12,
            "category": "Картриджи"
        },
        
        # Тонеры
        {
            "name": "ТОНЕР ЧЁРНЫЙ C60",
            "sku": "C60-TONE",
            "purchase_price": "3500.00",
            "coefficient": "0.85",  # скидка 15%
            "quantity": 20,
            "category": "Тонеры"
        },
        {
            "name": "ТОНЕР СМЕШАННЫЙ 4 ЦВЕТА",
            "sku": "4COL-TONE",
            "purchase_price": "14000.00",
            "coefficient": "0.9",
            "quantity": 5,
            "category": "Тонеры"
        },
        
        # Расходники
        {
            "name": "ФОТОБАРАБАН",
            "sku": "DRUM-60",
            "purchase_price": "8500.00",
            "coefficient": "1.0",
            "quantity": 6,
            "category": "Расходники"
        },
        {
            "name": "ДОЗИРУЮЩЕЕ ЛЕЗВИЕ",
            "sku": "BLADE-BU",
            "purchase_price": "1200.00",
            "coefficient": "0.95",
            "quantity": 25,
            "category": "Расходники"
        },
        {
            "name": "БУНКЕР ОТХОДОВ",
            "sku": "WASTE-BIN",
            "purchase_price": "2000.00",
            "coefficient": "1.0",
            "quantity": 15,
            "category": "Расходники"
        },
        
        # С НДС
        {
            "name": "БУМАГА A4 (500 листов) + НДС",
            "sku": "PAPER-A4-500",
            "purchase_price": "350.00",
            "coefficient": "1.18",  # НДС 18%
            "quantity": 100,
            "category": "Бумага"
        },
        {
            "name": "КОНВЕРТЫ БЕЛЫЕ + НДС",
            "sku": "ENVELOPE-WHT",
            "purchase_price": "450.00",
            "coefficient": "1.18",  # НДС 18%
            "quantity": 50,
            "category": "Расходники"
        },
        
        # Запасные части
        {
            "name": "РЕМЕНЬ ПРИВОДА",
            "sku": "BELT-DRV",
            "purchase_price": "5000.00",
            "coefficient": "1.05",
            "quantity": 4,
            "category": "Запчасти"
        },
        {
            "name": "РОЛ ДАВЛЕНИЯ",
            "sku": "ROLLER-PR",
            "purchase_price": "6500.00",
            "coefficient": "1.0",
            "quantity": 3,
            "category": "Запчасти"
        },
        {
            "name": "ПОЛИМЕРНЫЙ РЕМЕНЬ",
            "sku": "POLY-BELT",
            "purchase_price": "7200.00",
            "coefficient": "1.05",
            "quantity": 2,
            "category": "Запчасти"
        },
        
        # Прочее
        {
            "name": "МАСЛО ДЛЯ ТОНЕРА",
            "sku": "TONER-OIL",
            "purchase_price": "2500.00",
            "coefficient": "0.9",
            "quantity": 10,
            "category": "Химия"
        },
        {
            "name": "СПРЕЙ ДЛЯ ЧИСТКИ",
            "sku": "CLEAN-SPRAY",
            "purchase_price": "1500.00",
            "coefficient": "0.95",
            "quantity": 20,
            "category": "Химия"
        },
        {
            "name": "САЛФЕТКИ МИКРОФИБРА",
            "sku": "MICRO-WIPE",
            "purchase_price": "800.00",
            "coefficient": "1.0",
            "quantity": 30,
            "category": "Расходники"
        },
        {
            "name": "ПАМЯТИ USB 3.0 (32GB)",
            "sku": "USB-32GB",
            "purchase_price": "600.00",
            "coefficient": "1.15",
            "quantity": 25,
            "category": "Периферия"
        },
    ]
    
    created_products = []
    
    for i, product in enumerate(products_data, 1):
        try:
            response = requests.post(
                f"{API_BASE_URL}/products",
                json=product,
                timeout=10
            )
            
            if response.status_code == 200:
                product_data = response.json()
                created_products.append(product_data)
                print_status(
                    f"[{i:2d}/{len(products_data)}] ✅ {product['name']} (ID: {product_data['id']})",
                    "SUCCESS"
                )
            else:
                print_status(
                    f"[{i:2d}/{len(products_data)}] ❌ {product['name']} - {response.status_code}",
                    "ERROR"
                )
                
        except Exception as e:
            print_status(f"[{i:2d}/{len(products_data)}] ❌ Ошибка: {e}", "ERROR")
        
        time.sleep(DELAY)
    
    print_status(f"✅ Создано товаров: {len(created_products)}/{len(products_data)}", "SUCCESS")
    return created_products

def create_sales(products):
    """Создать продажи"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}💰 СОЗДАНИЕ ПРОДАЖ{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    if len(products) < 2:
        print_status("❌ Недостаточно товаров для создания продаж", "ERROR")
        return
    
    clients = [
        "ООО Тестовая Компания",
        "АО Продакт",
        "ИП Сергеев С.И.",
        "ЗАО РегионПринтер",
        "ООО Офис Сервис",
        "ООО МашЧасть",
        "АО Диджитал Солюшен",
        "ООО КопиЦентр",
    ]
    
    statuses = ["UNPAID", "PAID", "PARTIAL"]
    created_sales = []
    sale_count = 0
    
    # Создаём 8-10 продаж
    for _ in range(9):
        client = random.choice(clients)
        status = random.choice(statuses)
        
        # Выбираем 2-4 случайных товара
        num_items = random.randint(2, 4)
        sale_items = []
        
        for _ in range(num_items):
            product = random.choice(products)
            
            # Случайная цена продажи (от закупки до закупки + 50%)
            base_price = float(product['purchase_price'])
            sold_price = base_price * random.uniform(1.1, 1.5)
            
            # Случайное количество (1-5 единиц)
            quantity = random.randint(1, 5)
            
            # Коэффициент продажи (может отличаться от закупочного)
            coef = round(random.uniform(0.9, 1.25), 2)
            
            sale_items.append({
                "product_id": product['id'],
                "quantity": quantity,
                "sold_price_per_unit": f"{sold_price:.2f}",
                "coefficient": str(coef)
            })
        
        sale_data = {
            "client_name": client,
            "items": sale_items
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/sales",
                json=sale_data,
                timeout=10
            )
            
            if response.status_code == 200:
                sale = response.json()
                created_sales.append(sale)
                sale_count += 1
                
                total = sale.get('total', 0)
                print_status(
                    f"[{sale_count:2d}] ✅ {client} - {total:,.2f} руб. ({status})",
                    "SUCCESS"
                )
                
                # Изменяем статус оплаты
                if status in ["PAID", "PARTIAL"]:
                    time.sleep(DELAY)
                    status_response = requests.put(
                        f"{API_BASE_URL}/sales/{sale['id']}/status",
                        json={"status": status},
                        timeout=10
                    )
                    if status_response.status_code == 200:
                        print_status(f"    └─ Статус изменён на: {status}", "INFO")
            else:
                print_status(f"❌ Ошибка при создании продажи: {response.status_code}", "ERROR")
                
        except Exception as e:
            print_status(f"❌ Ошибка: {e}", "ERROR")
        
        time.sleep(DELAY)
    
    print_status(f"✅ Создано продаж: {sale_count}", "SUCCESS")
    return created_sales

def get_statistics():
    """Получить статистику"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}📊 СТАТИСТИКА{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    try:
        # Получить товары
        products_response = requests.get(
            f"{API_BASE_URL}/products/all",
            timeout=10
        )
        
        if products_response.status_code == 200:
            products = products_response.json()
            total_products = len(products)
            total_quantity = sum(p.get('quantity', 0) for p in products)
            
            print_status(f"Товаров в системе: {total_products}", "INFO")
            print_status(f"Единиц на складе: {total_quantity}", "INFO")
        
        # Получить продажи
        sales_response = requests.get(
            f"{API_BASE_URL}/sales",
            timeout=10
        )
        
        if sales_response.status_code == 200:
            sales = sales_response.json()
            total_sales = len(sales)
            total_revenue = sum(s.get('total', 0) for s in sales)
            
            print_status(f"Продаж в системе: {total_sales}", "INFO")
            print_status(f"Общая выручка: {total_revenue:,.2f} руб.", "INFO")
            
            # Статусы
            statuses_count = {}
            for sale in sales:
                status = sale.get('status', 'UNKNOWN')
                statuses_count[status] = statuses_count.get(status, 0) + 1
            
            for status, count in statuses_count.items():
                print_status(f"  └─ {status}: {count}", "INFO")
        
        # История операций
        history_response = requests.get(
            f"{API_BASE_URL}/stock-history",
            timeout=10
        )
        
        if history_response.status_code == 200:
            history = history_response.json()
            print_status(f"Операций в истории: {len(history)}", "INFO")
            
    except Exception as e:
        print_status(f"❌ Ошибка при получении статистики: {e}", "ERROR")

def main():
    """Главная функция"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║    🚀 СКРИПТ ЗАПОЛНЕНИЯ БАЗЫ ДАННЫХ                  ║
    ║    Inventory Management System                        ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.ENDC}")
    
    # Проверяем API
    if not check_api_connection():
        return
    
    # Создаём товары
    products = create_products()
    
    if products:
        # Создаём продажи
        create_sales(products)
        
        # Выводим статистику
        time.sleep(1)
        get_statistics()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║    ✅ ПРОЦЕСС ЗАВЕРШЁН!                              ║
    ║                                                       ║
    ║    Откройте приложение:                              ║
    ║    👉 http://localhost:3000                          ║
    ║                                                       ║
    ║    API документация:                                 ║
    ║    👉 http://localhost:8000/docs                     ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_status("\n⏸ Прервано пользователем", "WARNING")
    except Exception as e:
        print_status(f"\n❌ Критическая ошибка: {e}", "ERROR")
