from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ──────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str


class TokenData(BaseModel):
    usuario_id: int
    rol: str


# ── Rol ───────────────────────────────────────────────────────────────────────

class RolOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Usuario ───────────────────────────────────────────────────────────────────

class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    activo: bool
    rol: RolOut

    model_config = {"from_attributes": True}


# ── Categoría ─────────────────────────────────────────────────────────────────

class CategoriaOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    model_config = {"from_attributes": True}


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


# ── Producto ──────────────────────────────────────────────────────────────────

class ProductoOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    precio_compra: Decimal
    precio_venta: Decimal
    stock_actual: int
    stock_minimo: int
    stock_bajo: bool
    imagen_url: Optional[str] = None
    activo: bool
    categoria: CategoriaOut

    model_config = {"from_attributes": True}


class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    precio_compra: Decimal
    precio_venta: Decimal
    stock_actual: int = 0
    stock_minimo: int = 5
    categoria_id: int


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo_barras: Optional[str] = None
    precio_compra: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    stock_minimo: Optional[int] = None
    categoria_id: Optional[int] = None


# ── Proveedor ─────────────────────────────────────────────────────────────────

class ProveedorOut(BaseModel):
    id: int
    nombre: str
    rfc: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool

    model_config = {"from_attributes": True}


class ProveedorCreate(BaseModel):
    nombre: str
    rfc: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None

    @field_validator("rfc")
    @classmethod
    def rfc_upper(cls, v: str) -> str:
        return v.upper()


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    rfc: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None

    @field_validator("rfc")
    @classmethod
    def rfc_upper(cls, v: Optional[str]) -> Optional[str]:
        return v.upper() if v else v


# ── Cliente ───────────────────────────────────────────────────────────────────

class ClienteOut(BaseModel):
    id: int
    razon_social: str
    rfc: str
    regimen_fiscal: str
    uso_cfdi: str
    direccion_fiscal: str
    codigo_postal: str
    email: str
    telefono: Optional[str] = None
    activo: bool

    model_config = {"from_attributes": True}


class ClienteCreate(BaseModel):
    razon_social: str
    rfc: str
    regimen_fiscal: str
    uso_cfdi: str = "G03"
    direccion_fiscal: str
    codigo_postal: str
    email: str
    telefono: Optional[str] = None

    @field_validator("rfc")
    @classmethod
    def rfc_upper(cls, v: str) -> str:
        return v.upper()


class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = None
    regimen_fiscal: Optional[str] = None
    uso_cfdi: Optional[str] = None
    direccion_fiscal: Optional[str] = None
    codigo_postal: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None


# ── Venta ─────────────────────────────────────────────────────────────────────

class ItemVentaIn(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: Decimal


class VentaCreate(BaseModel):
    items: list[ItemVentaIn]
    metodo_pago: str = "Efectivo"
    monto_recibido: Optional[Decimal] = None
    cliente_id: Optional[int] = None


class DetalleVentaOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class VentaOut(BaseModel):
    id: int
    folio: str
    usuario_id: int
    cliente_id: Optional[int] = None
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    metodo_pago: str
    monto_recibido: Optional[Decimal] = None
    cambio: Optional[Decimal] = None
    estado: str
    facturada: bool
    fecha: datetime
    detalles: list[DetalleVentaOut] = []

    model_config = {"from_attributes": True}


class VentaCreatedOut(BaseModel):
    venta_id: int
    folio: str
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    cambio: Decimal


# ── Entrada de Inventario ─────────────────────────────────────────────────────

class ItemEntradaIn(BaseModel):
    producto_id: int
    cantidad: int
    costo_unitario: Decimal


class EntradaCreate(BaseModel):
    proveedor_id: int
    items: list[ItemEntradaIn]
    observaciones: Optional[str] = None


class DetalleEntradaOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    costo_unitario: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class EntradaOut(BaseModel):
    id: int
    folio: str
    proveedor_id: int
    usuario_id: int
    total: Decimal
    observaciones: Optional[str] = None
    fecha: datetime
    detalles: list[DetalleEntradaOut] = []

    model_config = {"from_attributes": True}


# ── Cierre de Caja ────────────────────────────────────────────────────────────

class CierreCajaCreate(BaseModel):
    fecha: date
    efectivo_contado: Decimal
    nota: Optional[str] = None


class CierreCajaOut(BaseModel):
    id: int
    usuario_id: int
    fecha: date
    total_ventas_efectivo: Decimal
    total_ventas_tarjeta: Decimal
    total_ventas: Decimal
    num_transacciones: int
    efectivo_contado: Decimal
    diferencia: Decimal
    nota: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Reportes ──────────────────────────────────────────────────────────────────

class VentaDiariaOut(BaseModel):
    fecha: date
    total_ventas: Decimal
    num_transacciones: int


class StockBajoOut(BaseModel):
    id: int
    nombre: str
    stock_actual: int
    stock_minimo: int
    categoria: str
