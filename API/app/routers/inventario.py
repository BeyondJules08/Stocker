from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_rol
from app.models import (
    DetalleEntrada, EntradaInventario, Producto, Proveedor, Usuario,
)
from app.schemas import (
    EntradaCreate, EntradaOut,
    ProveedorCreate, ProveedorOut, ProveedorUpdate,
)

router = APIRouter(prefix="/inventario", tags=["Inventario"])


def _generar_folio_entrada(db: Session) -> str:
    hoy = date.today()
    inicio_dia = datetime.combine(hoy, datetime.min.time())
    count = db.query(func.count(EntradaInventario.id)).filter(
        EntradaInventario.fecha >= inicio_dia
    ).scalar()
    return f"ENT-{hoy.strftime('%Y%m%d')}-{count + 1:04d}"


# ── Proveedores ───────────────────────────────────────────────────────────────

@router.get("/proveedores", response_model=list[ProveedorOut])
def listar_proveedores(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return db.query(Proveedor).filter(Proveedor.activo == True).order_by(Proveedor.nombre).all()


@router.get("/proveedores/{prov_id}", response_model=ProveedorOut)
def obtener_proveedor(
    prov_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    prov = db.get(Proveedor, prov_id)
    if not prov or not prov.activo:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return prov


@router.post("/proveedores", response_model=ProveedorOut, status_code=status.HTTP_201_CREATED)
def crear_proveedor(
    data: ProveedorCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    dup = db.query(Proveedor).filter(Proveedor.rfc == data.rfc).first()
    if dup:
        raise HTTPException(status_code=400, detail="RFC ya registrado")
    prov = Proveedor(**data.model_dump())
    db.add(prov)
    db.commit()
    db.refresh(prov)
    return prov


@router.put("/proveedores/{prov_id}", response_model=ProveedorOut)
def actualizar_proveedor(
    prov_id: int,
    data: ProveedorUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    prov = db.get(Proveedor, prov_id)
    if not prov or not prov.activo:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(prov, field, value)
    db.commit()
    db.refresh(prov)
    return prov


@router.delete("/proveedores/{prov_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proveedor(
    prov_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    prov = db.get(Proveedor, prov_id)
    if not prov or not prov.activo:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    prov.activo = False
    db.commit()


# ── Entradas de inventario ────────────────────────────────────────────────────

@router.get("/entradas", response_model=list[EntradaOut])
def listar_entradas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    return (
        db.query(EntradaInventario)
        .order_by(EntradaInventario.fecha.desc())
        .all()
    )


@router.get("/entradas/{entrada_id}", response_model=EntradaOut)
def obtener_entrada(
    entrada_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("almacen", "gerente")),
):
    entrada = db.get(EntradaInventario, entrada_id)
    if not entrada:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    return entrada


@router.post("/entradas", response_model=EntradaOut, status_code=status.HTTP_201_CREATED)
def crear_entrada(
    data: EntradaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_rol("almacen")),
):
    if not data.items:
        raise HTTPException(status_code=400, detail="La entrada no tiene productos")

    prov = db.get(Proveedor, data.proveedor_id)
    if not prov or not prov.activo:
        raise HTTPException(status_code=400, detail="Proveedor no válido")

    for item in data.items:
        prod = db.get(Producto, item.producto_id)
        if not prod or not prod.activo:
            raise HTTPException(
                status_code=400, detail=f"Producto no válido: {item.producto_id}"
            )

    entrada = EntradaInventario(
        folio=_generar_folio_entrada(db),
        proveedor_id=data.proveedor_id,
        usuario_id=current_user.id,
        total=Decimal("0"),
        observaciones=data.observaciones,
    )
    db.add(entrada)
    db.flush()

    total = Decimal("0")
    for item in data.items:
        subtotal = item.costo_unitario * item.cantidad
        total += subtotal
        det = DetalleEntrada(
            entrada_id=entrada.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            costo_unitario=item.costo_unitario,
            subtotal=subtotal,
        )
        db.add(det)
        prod = db.get(Producto, item.producto_id)
        prod.stock_actual += item.cantidad

    entrada.total = total
    db.commit()
    db.refresh(entrada)
    return entrada
