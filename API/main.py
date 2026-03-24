from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, clientes, inventario, productos, reportes, ventas

app = FastAPI(
    title="Stocker API",
    description="REST API for the Stocker POS + Inventory system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(ventas.router)
app.include_router(inventario.router)
app.include_router(reportes.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "stocker-api"}
