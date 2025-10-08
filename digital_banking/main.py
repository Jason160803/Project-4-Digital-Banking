from fastapi import FastAPI
from .routers import admin, customer

app = FastAPI(
    title="Project 4: Digital Banking API",
    description="API for a simple banking service as part of the Kapita Selekta Analitika Data course.",
    version="1.0.0"
)

# Include routers
app.include_router(admin.router)
app.include_router(customer.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Digital Banking API"}