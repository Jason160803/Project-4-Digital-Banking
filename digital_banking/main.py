from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import admin, customer

app = FastAPI(
    title="Project 4: Digital Banking API",
    description="API for a simple banking service.",
    version="1.0.0"
)

# Menambahkan middleware untuk CORS
origins = ["*"] # Mengizinkan semua origin

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin.router)
app.include_router(customer.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Digital Banking API"}