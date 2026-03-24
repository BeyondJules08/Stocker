from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_rol
from app.models import CierreCaja, Producto, Usuario, Venta
from app.schemas import CierreCajaCreate, CierreCajaOut, StockBajoOut, VentaDiariaOut

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/ventas-por-dia", response_model=list[VentaDiariaOut])
def ventas_por_dia(
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("gerente")),
):
    query = db.query(
        func.date(Venta.fecha).label("fecha"),
        func.sum(Venta.total).label("total_ventas"),
        func.count(Venta.id).label("num_transacciones"),
    ).filter(Venta.estado == "completada")

    if desde:
        query = query.filter(func.date(Venta.fecha) >= desde)
    if hasta:
        query = query.filter(func.date(Venta.fecha) <= hasta)

    rows = query.group_by(func.date(Venta.fecha)).order_by(func.date(Venta.fecha).desc()).all()

    return [
        VentaDiariaOut(
            fecha=row.fecha,
            total_ventas=row.total_ventas or Decimal("0"),
            num_transacciones=row.num_transacciones,
        )
        for row in rows
    ]


@router.get("/stock-bajo", response_model=list[StockBajoOut])
def stock_bajo(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("gerente", "almacen")),
):
    productos = (
        db.query(Producto)
        .filter(Producto.activo == True)
        .filter(Producto.stock_actual <= Producto.stock_minimo)
        .order_by(Producto.stock_actual)
        .all()
    )
    return [
        StockBajoOut(
            id=p.id,
            nombre=p.nombre,
            stock_actual=p.stock_actual,
            stock_minimo=p.stock_minimo,
            categoria=p.categoria.nombre,
        )
        for p in productos
    ]


@router.get("/resumen-hoy")
def resumen_hoy(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("gerente")),
):
    hoy = date.today()
    row = db.query(
        func.coalesce(func.sum(Venta.total), 0).label("total"),
        func.coalesce(func.sum(Venta.iva), 0).label("iva"),
        func.count(Venta.id).label("num_ventas"),
    ).filter(
        func.date(Venta.fecha) == hoy,
        Venta.estado == "completada",
    ).first()

    return {
        "fecha": hoy,
        "total_ventas": float(row.total),
        "total_iva": float(row.iva),
        "num_transacciones": row.num_ventas,
    }


# ── Cierre de Caja ────────────────────────────────────────────────────────────

@router.get("/cierres-caja", response_model=list[CierreCajaOut])
def listar_cierres(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("gerente")),
):
    return db.query(CierreCaja).order_by(CierreCaja.fecha.desc()).all()


@router.post("/cierres-caja", response_model=CierreCajaOut, status_code=201)
def registrar_cierre(
    data: CierreCajaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_rol("operativo")),
):
    # Aggregate today's sales
    row = db.query(
        func.coalesce(
            func.sum(Venta.total.filter(Venta.metodo_pago == "Efectivo")), 0
        ).label("efectivo"),
        func.coalesce(
            func.sum(Venta.total.filter(Venta.metodo_pago != "Efectivo")), 0
        ).label("tarjeta"),
        func.coalesce(func.sum(Venta.total), 0).label("total"),
        func.count(Venta.id).label("count"),
    ).filter(
        func.date(Venta.fecha) == data.fecha,
        Venta.usuario_id == current_user.id,
        Venta.estado == "completada",
    ).first()

    diferencia = (data.efectivo_contado - Decimal(str(row.efectivo))).quantize(
        Decimal("0.01")
    )

    cierre = CierreCaja(
        usuario_id=current_user.id,
        fecha=data.fecha,
        total_ventas_efectivo=row.efectivo,
        total_ventas_tarjeta=row.tarjeta,
        total_ventas=row.total,
        num_transacciones=row.count,
        efectivo_contado=data.efectivo_contado,
        diferencia=diferencia,
        nota=data.nota,
    )
    db.add(cierre)
    db.commit()
    db.refresh(cierre)
    return cierre
