from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import products, sales, import_excel
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory & Sales API",
    description="Полный учёт склада и продаж с Excel-импортом, историей и коэффициентами",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api", tags=["📦 Склад"])
app.include_router(sales.router, prefix="/api", tags=["💰 Продажи"])
app.include_router(import_excel.router, prefix="/api", tags=["📤 Импорт"])