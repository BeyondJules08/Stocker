from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    productos = db.relationship('Producto', backref='categoria', lazy=True)


class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    codigo_barras = db.Column(db.String(50), unique=True)
    precio_compra = db.Column(db.Numeric(12, 2), nullable=False)
    precio_venta = db.Column(db.Numeric(12, 2), nullable=False)
    stock_actual = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=5)
    imagen_url = db.Column(db.String(500))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo


class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    rfc = db.Column(db.String(13), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(150))
    direccion = db.Column(db.String(300))
    activo = db.Column(db.Boolean, default=True)


class EntradaInventario(db.Model):
    __tablename__ = 'entradas_inventario'
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True, nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    observaciones = db.Column(db.Text)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    proveedor = db.relationship('Proveedor', backref='entradas')
    usuario = db.relationship('Usuario', backref='entradas')
    detalles = db.relationship('DetalleEntrada', backref='entrada', lazy=True,
                               cascade='all, delete-orphan')


class DetalleEntrada(db.Model):
    __tablename__ = 'detalle_entrada'
    id = db.Column(db.Integer, primary_key=True)
    entrada_id = db.Column(db.Integer, db.ForeignKey('entradas_inventario.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    producto = db.relationship('Producto', backref='detalles_entrada')


class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(200), nullable=False)
    rfc = db.Column(db.String(13), unique=True, nullable=False)
    regimen_fiscal = db.Column(db.String(100), nullable=False)
    uso_cfdi = db.Column(db.String(10), nullable=False, default='G03')
    direccion_fiscal = db.Column(db.String(300), nullable=False)
    codigo_postal = db.Column(db.String(5), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20))
    activo = db.Column(db.Boolean, default=True)


class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    iva = db.Column(db.Numeric(12, 2), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)
    monto_recibido = db.Column(db.Numeric(12, 2))
    cambio = db.Column(db.Numeric(12, 2))
    estado = db.Column(db.String(20), nullable=False, default='completada')
    facturada = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario = db.relationship('Usuario', backref='ventas')
    cliente = db.relationship('Cliente', backref='ventas')
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True,
                               cascade='all, delete-orphan')
    factura = db.relationship('Factura', backref='venta', uselist=False)


class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    producto = db.relationship('Producto', backref='detalles_venta')


class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    folio_fiscal = db.Column(db.String(36), unique=True, nullable=False)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    xml_url = db.Column(db.String(500), nullable=False)
    pdf_url = db.Column(db.String(500), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    iva = db.Column(db.Numeric(12, 2), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cliente = db.relationship('Cliente', backref='facturas')


class CierreCaja(db.Model):
    __tablename__ = 'cierres_caja'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    total_ventas_efectivo = db.Column(db.Numeric(12, 2), nullable=False)
    total_ventas_tarjeta = db.Column(db.Numeric(12, 2), nullable=False)
    total_ventas = db.Column(db.Numeric(12, 2), nullable=False)
    num_transacciones = db.Column(db.Integer, nullable=False)
    efectivo_contado = db.Column(db.Numeric(12, 2), nullable=False)
    diferencia = db.Column(db.Numeric(12, 2), nullable=False)
    nota = db.Column(db.Text)
    usuario = db.relationship('Usuario', backref='cierres')


class LogAuditoria(db.Model):
    __tablename__ = 'log_auditoria'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    entidad = db.Column(db.String(50), nullable=False)
    entidad_id = db.Column(db.Integer)
    detalle = db.Column(db.JSON)
    ip = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario = db.relationship('Usuario', backref='logs')
