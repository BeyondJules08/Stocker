-- ============================================================
-- Stocker - Database Initialization Script
-- ============================================================
CREATE DATABASE IF NOT EXISTS stocker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stocker;
SET NAMES utf8mb4;

-- ============================================================
-- TABLE: roles
-- ============================================================
CREATE TABLE IF NOT EXISTS roles (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(50)  UNIQUE NOT NULL,
    descripcion VARCHAR(200),
    activo      BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLE: usuarios
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol_id        INT NOT NULL,
    activo        BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMP NULL,
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- ============================================================
-- TABLE: categorias
-- ============================================================
CREATE TABLE IF NOT EXISTS categorias (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) UNIQUE NOT NULL,
    descripcion VARCHAR(255),
    activo      BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLE: productos
-- ============================================================
CREATE TABLE IF NOT EXISTS productos (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(150) NOT NULL,
    descripcion    TEXT,
    codigo_barras  VARCHAR(50)  UNIQUE,
    precio_compra  DECIMAL(12,2) NOT NULL,
    precio_venta   DECIMAL(12,2) NOT NULL,
    stock_actual   INT NOT NULL DEFAULT 0,
    stock_minimo   INT NOT NULL DEFAULT 5,
    imagen_url     VARCHAR(500),
    categoria_id   INT NOT NULL,
    activo         BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_productos_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- ============================================================
-- TABLE: proveedores
-- ============================================================
CREATE TABLE IF NOT EXISTS proveedores (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nombre    VARCHAR(150) NOT NULL,
    rfc       VARCHAR(13)  UNIQUE NOT NULL,
    telefono  VARCHAR(20),
    email     VARCHAR(150),
    direccion VARCHAR(300),
    activo    BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLE: entradas_inventario
-- ============================================================
CREATE TABLE IF NOT EXISTS entradas_inventario (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    folio         VARCHAR(20) UNIQUE NOT NULL,
    proveedor_id  INT NOT NULL,
    usuario_id    INT NOT NULL,
    total         DECIMAL(12,2) NOT NULL,
    observaciones TEXT,
    fecha         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_entrada_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
    CONSTRAINT fk_entrada_usuario   FOREIGN KEY (usuario_id)   REFERENCES usuarios(id)
);

-- ============================================================
-- TABLE: detalle_entrada
-- ============================================================
CREATE TABLE IF NOT EXISTS detalle_entrada (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    entrada_id      INT NOT NULL,
    producto_id     INT NOT NULL,
    cantidad        INT           NOT NULL,
    costo_unitario  DECIMAL(12,2) NOT NULL,
    subtotal        DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_det_entrada  FOREIGN KEY (entrada_id)  REFERENCES entradas_inventario(id),
    CONSTRAINT fk_det_producto FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- ============================================================
-- TABLE: clientes
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    razon_social     VARCHAR(200) NOT NULL,
    rfc              VARCHAR(13)  UNIQUE NOT NULL,
    regimen_fiscal   VARCHAR(100) NOT NULL,
    uso_cfdi         VARCHAR(10)  NOT NULL DEFAULT 'G03',
    direccion_fiscal VARCHAR(300) NOT NULL,
    codigo_postal    VARCHAR(5)   NOT NULL,
    email            VARCHAR(150) NOT NULL,
    telefono         VARCHAR(20),
    activo           BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLE: ventas
-- ============================================================
CREATE TABLE IF NOT EXISTS ventas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    folio           VARCHAR(20) UNIQUE NOT NULL,
    usuario_id      INT NOT NULL,
    cliente_id      INT,
    subtotal        DECIMAL(12,2) NOT NULL,
    iva             DECIMAL(12,2) NOT NULL,
    total           DECIMAL(12,2) NOT NULL,
    metodo_pago     VARCHAR(20)   NOT NULL,
    monto_recibido  DECIMAL(12,2),
    cambio          DECIMAL(12,2),
    estado          VARCHAR(20)   NOT NULL DEFAULT 'completada',
    facturada       BOOLEAN DEFAULT FALSE,
    fecha           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_venta_usuario  FOREIGN KEY (usuario_id)  REFERENCES usuarios(id),
    CONSTRAINT fk_venta_cliente  FOREIGN KEY (cliente_id)  REFERENCES clientes(id)
);

-- ============================================================
-- TABLE: detalle_venta
-- ============================================================
CREATE TABLE IF NOT EXISTS detalle_venta (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    venta_id         INT NOT NULL,
    producto_id      INT NOT NULL,
    cantidad         INT           NOT NULL,
    precio_unitario  DECIMAL(12,2) NOT NULL,
    subtotal         DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_dv_venta    FOREIGN KEY (venta_id)    REFERENCES ventas(id),
    CONSTRAINT fk_dv_producto FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- ============================================================
-- TABLE: facturas
-- ============================================================
CREATE TABLE IF NOT EXISTS facturas (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    folio_fiscal  VARCHAR(36) UNIQUE NOT NULL,
    venta_id      INT UNIQUE NOT NULL,
    cliente_id    INT NOT NULL,
    xml_url       VARCHAR(500) NOT NULL,
    pdf_url       VARCHAR(500) NOT NULL,
    subtotal      DECIMAL(12,2) NOT NULL,
    iva           DECIMAL(12,2) NOT NULL,
    total         DECIMAL(12,2) NOT NULL,
    fecha_emision TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_factura_venta   FOREIGN KEY (venta_id)   REFERENCES ventas(id),
    CONSTRAINT fk_factura_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- ============================================================
-- TABLE: cierres_caja
-- ============================================================
CREATE TABLE IF NOT EXISTS cierres_caja (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id              INT NOT NULL,
    fecha                   DATE NOT NULL,
    total_ventas_efectivo   DECIMAL(12,2) NOT NULL,
    total_ventas_tarjeta    DECIMAL(12,2) NOT NULL,
    total_ventas            DECIMAL(12,2) NOT NULL,
    num_transacciones       INT           NOT NULL,
    efectivo_contado        DECIMAL(12,2) NOT NULL,
    diferencia              DECIMAL(12,2) NOT NULL,
    nota                    TEXT,
    CONSTRAINT fk_cierre_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================================
-- TABLE: log_auditoria
-- ============================================================
CREATE TABLE IF NOT EXISTS log_auditoria (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    accion     VARCHAR(50)  NOT NULL,
    entidad    VARCHAR(50)  NOT NULL,
    entidad_id INT,
    detalle    JSON,
    ip         VARCHAR(45),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================================
-- SEED DATA
-- ============================================================

-- Roles
INSERT INTO roles (nombre, descripcion) VALUES
    ('gerente',   'Dueño o gerente: acceso a reportes y administración'),
    ('operativo', 'Cajero/Vendedor: ventas, facturas y cierre de caja'),
    ('almacen',   'Encargado de almacén: inventario, proveedores y entradas');

-- Usuarios (passwords: Admin123!, Operativo1!, Almacen1!)
-- Generated with werkzeug pbkdf2:sha256 equivalent — replaced at runtime by seed
INSERT INTO usuarios (nombre, email, password_hash, rol_id) VALUES
    ('Gerente Admin',   'gerente@stocker.com',   'pbkdf2:sha256:600000$stocker$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 1),
    ('Carlos Cajero',   'operativo@stocker.com', 'pbkdf2:sha256:600000$stocker$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 2),
    ('Ana Almacén',     'almacen@stocker.com',   'pbkdf2:sha256:600000$stocker$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 3);

-- Categorías
INSERT INTO categorias (nombre, descripcion) VALUES
    ('Bebidas',      'Refrescos, agua, jugos y bebidas en general'),
    ('Snacks',       'Botanas, papas, galletas y golosinas'),
    ('Lácteos',      'Leche, queso, yogurt y derivados'),
    ('Abarrotes',    'Artículos básicos de despensa'),
    ('Limpieza',     'Productos de limpieza del hogar'),
    ('Higiene',      'Artículos de higiene personal');

-- Proveedores
INSERT INTO proveedores (nombre, rfc, telefono, email, direccion) VALUES
    ('Distribuidora Norte SA', 'DNO800101AAA', '8001234567', 'ventas@disnorte.com', 'Av. Industrial 100, CDMX'),
    ('Abarrotes Gómez SA',     'AGO750615BBB', '5551234567', 'pedidos@gomez.com',   'Calle Comercio 22, Monterrey'),
    ('Lácteos del Valle',      'LVA900320CCC', '3121234567', 'info@lacteosvalle.mx', 'Blvd. Lechero 45, Guadalajara');

-- Productos de muestra
INSERT INTO productos (nombre, descripcion, codigo_barras, precio_compra, precio_venta, stock_actual, stock_minimo, categoria_id) VALUES
    ('Coca-Cola 600ml',       'Refresco de cola 600ml',         '7501055300897', 10.00, 16.00, 48, 10, 1),
    ('Agua 1.5L',             'Agua purificada 1.5 litros',     '7501055361414', 8.00,  12.00, 30, 10, 1),
    ('Sabritas Original 45g', 'Papas fritas sabor original',    '7501011304066', 9.50,  15.00, 24, 5,  2),
    ('Leche Lala 1L',         'Leche entera 1 litro',           '7501055311848', 18.00, 25.00,  4, 6,  3),
    ('Arroz 1kg',             'Arroz grano largo 1 kilogramo',  '7501055389479', 22.00, 32.00, 15, 5,  4),
    ('Jabón Ariel 500g',      'Detergente en polvo 500 gramos', '7500435141376', 35.00, 48.00,  8, 3,  5),
    ('Shampoo Head 400ml',    'Shampoo anticaspa 400ml',        '7500435043153', 55.00, 75.00,  6, 3,  6),
    ('Pepsi 600ml',           'Refresco de cola 600ml',         '7501055309395', 10.00, 16.00, 36, 10, 1),
    ('Galletas Oreo',         'Galletas de chocolate con crema','7622201398481', 14.00, 20.00, 20, 5,  2),
    ('Fanta Naranja 600ml',   'Refresco de naranja 600ml',      '7501055359633', 10.00, 16.00, 12, 10, 1);

-- Cliente genérico (público en general)
INSERT INTO clientes (razon_social, rfc, regimen_fiscal, uso_cfdi, direccion_fiscal, codigo_postal, email) VALUES
    ('Público en General', 'XAXX010101000', 'Sin obligaciones fiscales', 'S01', 'México', '00000', 'publico@general.com');
