# Stocker — Sistema de Gestión Comercial

Sistema web para centralizar el ciclo de venta de un negocio, desde que el producto entra al almacén hasta que se entrega la factura al cliente. Permite al dueño del negocio tomar decisiones basadas en reportes financieros.

---

## Arquitectura del Sistema

El proyecto está compuesto por **dos aplicaciones web independientes** que comparten una base de datos MySQL.

```
Stocker/
├── Flask/                  # App operativa (Python/Flask)  → Puerto 5000
├── Laravel/                # Panel gerencial (PHP/Laravel) → Puerto 8080
│   ├── stocker-admin/      # Proyecto Laravel
│   └── nginx.conf          # Proxy Nginx para Laravel
├── database/
│   └── init.sql            # Esquema MySQL + datos semilla
└── docker-compose.yml      # Orquestación completa
```

| Sistema | Tecnología | Puerto | Usuarios |
|---|---|---|---|
| Flask | Python 3.12 + Flask 3.1 | 5000 | Operativo, Almacén |
| Laravel | PHP 8.4 + Laravel 12 + Nginx | 8080 | Gerente |
| MySQL | MySQL 8.0 | 3306 | (compartida) |

---

## Módulos

### Flask — Usuario Operativo (Cajero/Vendedor)

| Módulo | Descripción |
|---|---|
| **Nueva Venta** | Punto de venta con búsqueda de productos por nombre o código de barras, carrito interactivo, cobro en efectivo o tarjeta, generación de ticket PDF |
| **Historial de Ventas** | Listado de ventas del día con totales y estado de facturación |
| **Facturas** | Generación de factura electrónica simulada (PDF formal + XML con estructura CFDI 4.0), listado de facturas emitidas |
| **Cierre de Caja** | Resumen automático del día (efectivo, tarjeta, transacciones), ingreso del efectivo contado, cálculo de diferencias, gráfica de ventas de los últimos 7 días |

### Flask — Encargado de Almacén

| Módulo | Descripción |
|---|---|
| **Dashboard** | Alertas de stock bajo, estadísticas generales |
| **Productos** | Catálogo completo con código de barras, categoría, precios de compra/venta, niveles de stock |
| **Categorías** | Gestión de categorías de productos |
| **Proveedores** | Directorio de proveedores con RFC y datos de contacto |
| **Entradas de Inventario** | Registro de compras a proveedores con actualización automática de stock |

### Laravel — Gerente / Panel de Reportes

| Módulo | Descripción |
|---|---|
| **Dashboard** | Resumen del mes: ventas, facturas, stock bajo. Gráfica de 7 días y top 5 productos |
| **Reporte de Ventas** | Filtro por rango de fechas, gráfica diaria, tabla detallada, exportación CSV |
| **Productos Más Vendidos** | Top 10 con gráfica horizontal, unidades e ingresos por producto |
| **Gráfica Mensual** | Comparativa de Ventas vs Gastos (entradas de inventario) en los últimos 12 meses, tabla de utilidad bruta y margen |
| **Cierres de Caja** | Historial de cierres con filtros, diferencias color-coded (verde/rojo/amarillo) |

---

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/)
- Git

---

## Guía de Instalación Paso a Paso

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Stocker
```

### 2. Construir y levantar los contenedores

```bash
docker compose up -d --build
```

Esto levanta cuatro contenedores:
- `stocker_db` — MySQL 8.0 (inicializa el esquema y los datos semilla automáticamente)
- `stocker_flask` — Aplicación Flask
- `stocker_laravel` — PHP-FPM con Laravel
- `stocker_nginx` — Proxy Nginx para Laravel

> La primera vez tarda varios minutos mientras se descargan las imágenes base y se instalan las dependencias.

### 3. Esperar a que MySQL esté listo

MySQL puede tardar ~30 segundos en estar disponible. Puedes verificarlo con:

```bash
docker compose exec db mysqladmin ping -h localhost -u stocker -pstocker123
```

Cuando responda `mysqladmin: [Warning] ...  mysqld is alive`, continúa.

### 4. Ejecutar las migraciones de Laravel

Crea las tablas que Laravel necesita para autenticación (`users`, `sessions`, `cache`, `jobs`). Las tablas del esquema Stocker ya existen gracias a `init.sql` y se omiten automáticamente.

```bash
docker compose exec laravel php artisan migrate --path=database/migrations/0001_01_01_000000_create_users_table.php --force
docker compose exec laravel php artisan migrate --path=database/migrations/0001_01_01_000001_create_cache_table.php --force
docker compose exec laravel php artisan migrate --path=database/migrations/0001_01_01_000002_create_jobs_table.php --force
```

### 5. Crear el usuario Gerente en Laravel

```bash
docker compose exec laravel php artisan db:seed
```

### 6. Establecer las contraseñas de Flask

El `init.sql` incluye hashes de contraseña provisionales. Este comando los reemplaza con hashes correctos de werkzeug:

```bash
docker compose exec flask python seed_passwords.py
```

### 7. Acceder a los sistemas

| Sistema | URL | Usuario | Contraseña |
|---|---|---|---|
| Flask (Operativo) | http://localhost:5000 | operativo@stocker.com | `Operativo1!` |
| Flask (Almacén) | http://localhost:5000 | almacen@stocker.com | `Almacen1!` |
| Laravel (Gerente) | http://localhost:8080 | gerente@stocker.com | `Admin123!` |

---

## Comandos Útiles

### Ver logs de un servicio

```bash
docker compose logs -f flask
docker compose logs -f laravel
docker compose logs -f db
```

### Reiniciar un servicio

```bash
docker compose restart flask
docker compose restart laravel
```

### Detener todo sin borrar datos

```bash
docker compose down
```

### Detener y borrar todos los volúmenes (reinicio completo)

> **Advertencia:** esto elimina todos los datos de la base de datos.

```bash
docker compose down -v
```

### Conectarse a la base de datos

```bash
docker compose exec db mysql -u stocker -pstocker123 stocker
```

---

## Base de Datos

La base de datos `stocker` se inicializa automáticamente con `database/init.sql` al primer arranque de MySQL.

### Tablas del esquema

| Tabla | Descripción |
|---|---|
| `roles` | Roles del sistema (gerente, operativo, almacen) |
| `usuarios` | Usuarios del sistema Flask |
| `categorias` | Categorías de productos |
| `productos` | Catálogo de productos con stock |
| `proveedores` | Directorio de proveedores |
| `entradas_inventario` | Cabecera de entradas de stock |
| `detalle_entrada` | Líneas de cada entrada de stock |
| `clientes` | Clientes con datos fiscales (CFDI) |
| `ventas` | Cabecera de ventas/tickets |
| `detalle_venta` | Líneas de cada venta |
| `facturas` | Facturas electrónicas generadas |
| `cierres_caja` | Registros de cierre diario de caja |
| `log_auditoria` | Trazabilidad de acciones |

### Datos semilla incluidos

- 3 roles, 3 usuarios de prueba
- 6 categorías, 3 proveedores, 10 productos de muestra
- 1 cliente genérico (Público en General, RFC `XAXX010101000`)

---

## Stack Tecnológico

**Flask**
- Python 3.12 / Flask 3.1
- Flask-SQLAlchemy + PyMySQL (ORM y driver MySQL)
- Flask-Login (autenticación por sesión)
- ReportLab (generación de PDF — tickets y facturas)
- `xml.etree.ElementTree` (generación de XML CFDI 4.0 simulado)
- Bootstrap 5.3 + Bootstrap Icons + Chart.js (UI)

**Laravel**
- PHP 8.4 / Laravel 12
- Eloquent ORM
- Blade Templates
- Bootstrap 5.3 + Bootstrap Icons + Chart.js (UI)
- Nginx (servidor web / proxy)

**Infraestructura**
- MySQL 8.0
- Podman / Docker + Compose
- Volúmenes persistentes para MySQL, uploads y documentos generados

---

## Estructura de Archivos Relevantes

```
Stocker/
├── database/
│   └── init.sql                        # Esquema completo + datos semilla
├── docker-compose.yml                  # Compose raíz (todos los servicios)
│
├── Flask/
│   ├── Dockerfile
│   ├── docker-compose.yml              # Compose standalone Flask
│   ├── requirements.txt
│   ├── run.py                          # Punto de entrada
│   ├── config.py                       # Configuración (DB, rutas, claves)
│   ├── seed_passwords.py               # Script de inicialización de contraseñas
│   └── app/
│       ├── __init__.py                 # App factory
│       ├── models.py                   # Modelos SQLAlchemy
│       ├── routes/
│       │   ├── auth.py                 # Login / logout
│       │   ├── ventas.py               # POS y ventas
│       │   ├── facturas.py             # Facturación CFDI
│       │   ├── cierre_caja.py          # Cierre de caja diario
│       │   └── inventario.py           # Productos, proveedores, entradas
│       ├── templates/                  # Plantillas Jinja2 (Bootstrap 5)
│       ├── static/                     # CSS, uploads, documentos generados
│       └── utils/
│           ├── pdf_generator.py        # Tickets y facturas PDF (ReportLab)
│           └── xml_generator.py        # XML CFDI 4.0 simulado
│
└── Laravel/
    ├── nginx.conf                      # Configuración Nginx
    ├── docker-compose.yml              # Compose standalone Laravel
    └── stocker-admin/
        ├── Dockerfile
        ├── app/
        │   ├── Http/
        │   │   ├── Controllers/
        │   │   │   ├── Auth/LoginController.php
        │   │   │   └── Reportes/ReportesController.php
        │   │   └── Middleware/GerenteMiddleware.php
        │   └── Models/                 # Eloquent models (Venta, Producto, etc.)
        ├── database/
        │   ├── migrations/             # Migraciones (con guards hasTable)
        │   └── seeders/DatabaseSeeder.php
        └── resources/views/
            ├── layouts/app.blade.php   # Layout base con sidebar
            ├── auth/login.blade.php
            └── reportes/               # Dashboard, ventas, productos, mensual, cierres
```
