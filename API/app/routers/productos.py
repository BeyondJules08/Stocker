from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_rol
from app.models import Categoria, Producto, Usuario
from app.schemas import (
    CategoriaCreate, CategoriaOut,
    ProductoCreate, ProductoOut, ProductoUpdate,
)

router = APIRouter(prefix="/productos", tags=["Productos"])

# ── Categorías ────────────────────────────────────────────────────────────────

@router.get("/categorias", response_model=list[CategoriaOut])
def listar_categorias(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return db.query(Categoria).filter(Categoria.activo == True).all()


@router.post("/categorias", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    data: CategoriaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    exists = db.query(Categoria).filter(Categoria.nombre == data.nombre).first()
    if exists:
        raise HTTPException(status_code=400, detail="La categoría ya existe")
    cat = Categoria(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categorias/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    cat_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    cat = db.get(Categoria, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    cat.activo = False
    db.commit()


# ── Productos ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ProductoOut])
def listar_productos(
    q: Optional[str] = Query(None, description="Buscar por nombre o código de barras"),
    stock_bajo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    query = db.query(Producto).filter(Producto.activo == True)
    if q:
        query = query.filter(
            Producto.nombre.ilike(f"%{q}%") | (Producto.codigo_barras == q)
        )
    if stock_bajo is True:
        query = query.filter(Producto.stock_actual <= Producto.stock_minimo)
    return query.order_by(Producto.nombre).all()


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    prod = db.get(Producto, producto_id)
    if not prod or not prod.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    cat = db.get(Categoria, data.categoria_id)
    if not cat or not cat.activo:
        raise HTTPException(status_code=400, detail="Categoría no válida")
    if data.codigo_barras:
        dup = db.query(Producto).filter(
            Producto.codigo_barras == data.codigo_barras
        ).first()
        if dup:
            raise HTTPException(status_code=400, detail="Código de barras ya registrado")
    prod = Producto(**data.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    prod = db.get(Producto, producto_id)
    if not prod or not prod.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(prod, field, value)
    db.commit()
    db.refresh(prod)
    return prod


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    prod = db.get(Producto, producto_id)
    if not prod or not prod.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    prod.activo = False
    db.commit()
