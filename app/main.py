# app/main.py

from fastapi import FastAPI
# TAMBAHKAN IMPORT INI
from fastapi.middleware.cors import CORSMiddleware
from .routers import admin, customer

app = FastAPI(
    title="Digital Banking API",
    description="API sederhana untuk layanan perbankan digital.",
    version="1.0.0"
)

# TAMBAHKAN BLOK KODE INI
origins = [
    "http://localhost",
    "http://localhost:8080",
    "null", # Mengizinkan permintaan dari file lokal (file://)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Mengizinkan semua metode (GET, POST, dll.)
    allow_headers=["*"], # Mengizinkan semua header
)


# Include routers (ini sudah ada sebelumnya)
app.include_router(admin.router)
app.include_router(customer.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Selamat datang di Digital Banking API"}