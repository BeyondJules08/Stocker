from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, JSON, Numeric, String, Text,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200))
    activo = Column(Boolean, default=True)
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    activo = Column(Boolean, default=True)
    ultimo_acceso = Column(DateTime, nullable=True)

    rol = relationship("Rol", back_populates="usuarios")
    ventas = relationship("Venta", back_populates="usuario")
    entradas = relationship("EntradaInventario", back_populates="usuario")
    cierres = relationship("CierreCaja", back_populates="usuario")
    logs = relationship("LogAuditoria", back_populates="usuario")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255))
    activo = Column(Boolean, default=True)
    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    codigo_barras = Column(String(50), unique=True)
    precio_compra = Column(Numeric(12, 2), nullable=False)
    precio_venta = Column(Numeric(12, 2), nullable=False)
    stock_actual = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=5)
    imagen_url = Column(String(500))
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    activo = Column(Boolean, default=True)

    categoria = relationship("Categoria", back_populates="productos")

    @property
    def stock_bajo(self) -> bool:
        return self.stock_actual <= self.stock_minimo


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    rfc = Column(String(13), unique=True, nullable=False)
    telefono = Column(String(20))
    email = Column(String(150))
    direccion = Column(String(300))
    activo = Column(Boolean, default=True)
    entradas = relationship("EntradaInventario", back_populates="proveedor")


class EntradaInventario(Base):
    __tablename__ = "entradas_inventario"

    id = Column(Integer, primary_key=True)
    folio = Column(String(20), unique=True, nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    observaciones = Column(Text)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)

    proveedor = relationship("Proveedor", back_populates="entradas")
    usuario = relationship("Usuario", back_populates="entradas")
    detalles = relationship(
        "DetalleEntrada", back_populates="entrada", cascade="all, delete-orphan"
    )


class DetalleEntrada(Base):
    __tablename__ = "detalle_entrada"

    id = Column(Integer, primary_key=True)
    entrada_id = Column(Integer, ForeignKey("entradas_inventario.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)

    entrada = relationship("EntradaInventario", back_populates="detalles")
    producto = relationship("Producto")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    razon_social = Column(String(200), nullable=False)
    rfc = Column(String(13), unique=True, nullable=False)
    regimen_fiscal = Column(String(100), nullable=False)
    uso_cfdi = Column(String(10), nullable=False, default="G03")
    direccion_fiscal = Column(String(300), nullable=False)
    codigo_postal = Column(String(5), nullable=False)
    email = Column(String(150), nullable=False)
    telefono = Column(String(20))
    activo = Column(Boolean, default=True)

    ventas = relationship("Venta", back_populates="cliente")
    facturas = relationship("Factura", back_populates="cliente")


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    folio = Column(String(20), unique=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    subtotal = Column(Numeric(12, 2), nullable=False)
    iva = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    metodo_pago = Column(String(20), nullable=False)
    monto_recibido = Column(Numeric(12, 2))
    cambio = Column(Numeric(12, 2))
    estado = Column(String(20), nullable=False, default="completada")
    facturada = Column(Boolean, default=False)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="ventas")
    cliente = relationship("Cliente", back_populates="ventas")
    detalles = relationship(
        "DetalleVenta", back_populates="venta", cascade="all, delete-orphan"
    )
    factura = relationship("Factura", back_populates="venta", uselist=False)


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")


class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True)
    folio_fiscal = Column(String(36), unique=True, nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"), unique=True, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    xml_url = Column(String(500), nullable=False)
    pdf_url = Column(String(500), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    iva = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    fecha_emision = Column(DateTime, nullable=False, default=datetime.utcnow)

    venta = relationship("Venta", back_populates="factura")
    cliente = relationship("Cliente", back_populates="facturas")


class CierreCaja(Base):
    __tablename__ = "cierres_caja"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    total_ventas_efectivo = Column(Numeric(12, 2), nullable=False)
    total_ventas_tarjeta = Column(Numeric(12, 2), nullable=False)
    total_ventas = Column(Numeric(12, 2), nullable=False)
    num_transacciones = Column(Integer, nullable=False)
    efectivo_contado = Column(Numeric(12, 2), nullable=False)
    diferencia = Column(Numeric(12, 2), nullable=False)
    nota = Column(Text)

    usuario = relationship("Usuario", back_populates="cierres")


class LogAuditoria(Base):
    __tablename__ = "log_auditoria"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    accion = Column(String(50), nullable=False)
    entidad = Column(String(50), nullable=False)
    entidad_id = Column(Integer)
    detalle = Column(JSON)
    ip = Column(String(45))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="logs")
