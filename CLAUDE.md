# Context 
This is a project called Stocker, it is a web system for inventory management and sales. It is composed of three applications: Flask, Laravel and FastAPI. The Flask application is for the "Usuario Operativo" and "Encargado de Almacén", the Laravel application is for the "Gerente" and the FastAPI application is for the REST API. The database is MySQL.

## System Architecture

The project is composed of **three independent web applications** that share a MySQL database.

```
Stocker/
├── Flask/                  # Operational App (Python/Flask)  → Port 5000
├── Laravel/                # Managerial Panel (PHP/Laravel) → Port 8080
│   ├── stocker-admin/      # Laravel Project
│   └── nginx.conf          # Nginx Proxy for Laravel
├── API/                    # REST API (FastAPI)            → Port 8000
├── database/
│   └── init.sql            # MySQL Schema + Seed data
└── docker-compose.yml      # Complete Orchestration
```

| Sistema | Tecnología | Puerto | Usuarios |
|---|---|---|---|
| Flask | Python 3.12 + Flask 3.1 | 5000 | Operativo, Almacén |
| Laravel | PHP 8.4 + Laravel 12 + Nginx | 8080 | Gerente |
| FastAPI | Python 3.12 + FastAPI | 8000 | API REST |
| MySQL | MySQL 8.0 | 3306 | (shared) |

## Modules

### Flask — Operational (Cashier/Salesperson)

| Módulo | Descripción |
|---|---|
| **Nueva Venta** | Point of sale with product search by name or barcode, interactive cart, cash or card payment, PDF ticket generation |
| **Historial de Ventas** | List of sales of the day with totals and billing status |
| **Facturas** | Generation of simulated electronic invoice (formal PDF + XML with CFDI 4.0 structure), list of issued invoices |
| **Cierre de Caja** | Automatic summary of the day (cash, card, transactions), cash count, difference calculation, sales graph of the last 7 days |

### Flask — Warehouse Manager

| Módulo | Descripción |
|---|---|
| **Dashboard** | Low stock alerts, general statistics |
| **Productos** | Complete catalog with barcode, category, purchase/sale prices, stock levels |
| **Categorías** | Product category management |
| **Proveedores** | Supplier directory with RFC and contact information |
| **Entradas de Inventario** | Purchase registration from suppliers with automatic stock update |

### Laravel — Manager / Reports Panel

| Módulo | Descripción |
|---|---|
| **Dashboard** | Monthly summary: sales, invoices, low stock. 7-day graph and top 5 products |
| **Reporte de Ventas** | Filter by date range, daily graph, detailed table, CSV export |
| **Productos Más Vendidos** | Top 10 with horizontal graph, units and income per product |
| **Gráfica Mensual** | Comparison of Sales vs Expenses (inventory inputs) in the last 12 months, gross profit and margin table |
| **Cierres de Caja** | Closing history with filters, color-coded differences (green/red/yellow) |
| **Pronóstico de Demanda** | Daily demand prediction per product using Multiple Linear Regression (see ML section) |

---

## ML Module — Demand Forecasting

The managerial panel includes a machine learning module that predicts how many units will be sold daily per product, using real sales data from the system.
