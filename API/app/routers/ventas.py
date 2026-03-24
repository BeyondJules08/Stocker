from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_rol
from app.models import Cliente, DetalleVenta, Producto, Usuario, Venta
from app.schemas import VentaCreate, VentaCreatedOut, VentaOut

router = APIRouter(prefix="/ventas", tags=["Ventas"])

IVA_TASA = Decimal("0.16")


def _generar_folio_venta(db: Session) -> str:
    hoy = date.today()
    count = db.query(func.count(Venta.id)).filter(
        func.date(Venta.fecha) == hoy
    ).scalar()
    return f"VTA-{hoy.strftime('%Y%m%d')}-{count + 1:04d}"


@router.get("", response_model=list[VentaOut])
def listar_ventas(
    fecha: Optional[date] = Query(None, description="Filtrar por fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    query = db.query(Venta)
    if fecha:
        query = query.filter(func.date(Venta.fecha) == fecha)
    # Operativo only sees their own sales; gerente sees all
    if current_user.rol.nombre == "operativo":
        query = query.filter(Venta.usuario_id == current_user.id)
    return query.order_by(Venta.fecha.desc()).all()


@router.get("/{venta_id}", response_model=VentaOut)
def obtener_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    venta = db.get(Venta, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if current_user.rol.nombre == "operativo" and venta.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sin acceso a esta venta")
    return venta


@router.post("", response_model=VentaCreatedOut, status_code=status.HTTP_201_CREATED)
def crear_venta(
    data: VentaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_rol("operativo")),
):
    if not data.items:
        raise HTTPException(status_code=400, detail="La venta no tiene artículos")

    # Validate stock
    for item in data.items:
        prod = db.get(Producto, item.producto_id)
        if not prod or not prod.activo:
            raise HTTPException(
                status_code=400, detail=f"Producto no válido: {item.producto_id}"
            )
        if prod.stock_actual < item.cantidad:
            raise HTTPException(
                status_code=400, detail=f"Stock insuficiente para {prod.nombre}"
            )

    subtotal = sum(item.precio_unitario * item.cantidad for item in data.items)
    iva = (subtotal * IVA_TASA).quantize(Decimal("0.01"))
    total = subtotal + iva

    if data.metodo_pago == "Efectivo":
        if data.monto_recibido is None or data.monto_recibido < total:
            raise HTTPException(
                status_code=400,
                detail="Monto recibido insuficiente para el pago en efectivo",
            )
        cambio = (data.monto_recibido - total).quantize(Decimal("0.01"))
    else:
        cambio = Decimal("0.00")

    venta = Venta(
        folio=_generar_folio_venta(db),
        usuario_id=current_user.id,
        cliente_id=data.cliente_id,
        subtotal=subtotal,
        iva=iva,
        total=total,
        metodo_pago=data.metodo_pago,
        monto_recibido=data.monto_recibido if data.metodo_pago == "Efectivo" else None,
        cambio=cambio if data.metodo_pago == "Efectivo" else None,
        estado="completada",
        facturada=False,
    )
    db.add(venta)
    db.flush()

    for item in data.items:
        prod = db.get(Producto, item.producto_id)
        detalle = DetalleVenta(
            venta_id=venta.id,
            producto_id=prod.id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=item.precio_unitario * item.cantidad,
        )
        prod.stock_actual -= item.cantidad
        db.add(detalle)

    db.commit()

    return VentaCreatedOut(
        venta_id=venta.id,
        folio=venta.folio,
        subtotal=subtotal,
        iva=iva,
        total=total,
        cambio=cambio,
    )
