from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .routers import admin, customer
from . import config

app = FastAPI(
    title="Project 4: Digital Banking API",
    description="API for a simple banking service.",
    version="1.0.0"
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AppConfig(BaseModel):
    daily_transaction_limit: int
    minimum_balance: float
    max_transfer_amount: float
    inter_bank_transfer_fee: float

@app.get("/config/", response_model=AppConfig, tags=["Configuration"])
def get_app_config():
    """Mengembalikan konfigurasi aplikasi yang relevan untuk frontend."""
    return {
        "daily_transaction_limit": config.DAILY_TRANSACTION_LIMIT,
        "minimum_balance": config.MINIMUM_BALANCE,
        "max_transfer_amount": config.MAX_TRANSFER_AMOUNT,
        "inter_bank_transfer_fee": config.INTER_BANK_TRANSFER_FEE,
    }

# Include routers
app.include_router(admin.router)
app.include_router(customer.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Digital Banking API"}