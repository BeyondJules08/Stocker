<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>@yield('title', 'Stocker — Reportes')</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <style>
    body { margin: 0; background: #f0f2f5; font-family: 'Segoe UI', sans-serif; }
    .topbar {
      position: fixed; top: 0; left: 0; right: 0; height: 58px;
      background: #16213e; color: #fff; z-index: 200;
      display: flex; align-items: center; padding: 0 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,.4);
    }
    .topbar .brand { font-size: 1.3rem; font-weight: 700; color: #f5a623; margin-right: auto; letter-spacing: .5px; }
    .sidebar {
      position: fixed; top: 58px; left: 0; width: 240px;
      height: calc(100vh - 58px); background: #1a1a2e;
      overflow-y: auto; padding: 16px 0; z-index: 100;
      box-shadow: 2px 0 8px rgba(0,0,0,.2);
    }
    .sidebar .nav-link {
      color: rgba(255,255,255,.75); padding: 9px 20px;
      display: flex; align-items: center; gap: 10px;
      text-decoration: none; font-size: .9rem;
      transition: background .15s, color .15s;
    }
    .sidebar .nav-link:hover, .sidebar .nav-link.active {
      background: rgba(245,166,35,.15); color: #f5a623;
      border-right: 3px solid #f5a623;
    }
    .sidebar-section {
      font-size: .7rem; letter-spacing: 1px; text-transform: uppercase;
      color: rgba(255,255,255,.35); padding: 6px 20px 2px; margin: 0;
    }
    .main-content { margin-left: 240px; padding: 80px 28px 28px; min-height: 100vh; }
    .stat-card {
      background: #fff; border-radius: 12px; padding: 20px 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,.07); border-left: 4px solid #f5a623;
    }
    .stat-card .value { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; }
    .stat-card .label { font-size: .85rem; color: #6c757d; }
    .table-card {
      background: #fff; border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,.07); overflow: hidden;
    }
    .table-card .table { margin: 0; }
    .table-card .table thead th {
      background: #1a1a2e; color: #fff; font-weight: 600;
      font-size: .85rem; border: none;
    }
    .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
    .page-header h2 { color: #1a1a2e; font-weight: 700; margin: 0; }
  </style>
  @yield('head')
</head>
<body>
  <!-- Topbar -->
  <nav class="topbar">
    <span class="brand"><i class="bi bi-box-seam"></i> Stocker <small class="text-warning ms-2" style="font-size:.75rem">Panel Gerencial</small></span>
    <div class="d-flex align-items: center; gap: 3; gap-3">
      <span class="text-white-50 small">
        <i class="bi bi-person-circle"></i> {{ Auth::user()->name }}
        <span class="badge bg-warning text-dark ms-1">Gerente</span>
      </span>
      <form method="POST" action="{{ route('logout') }}" class="ms-3">
        @csrf
        <button type="submit" class="btn btn-sm btn-outline-light">
          <i class="bi bi-box-arrow-right"></i> Salir
        </button>
      </form>
    </div>
  </nav>

  <!-- Sidebar -->
  <div class="sidebar">
    <p class="sidebar-section">REPORTES</p>
    <a href="{{ route('reportes.index') }}"
       class="nav-link {{ request()->routeIs('reportes.index') ? 'active' : '' }}">
      <i class="bi bi-speedometer2"></i> Dashboard
    </a>
    <a href="{{ route('reportes.ventas') }}"
       class="nav-link {{ request()->routeIs('reportes.ventas') ? 'active' : '' }}">
      <i class="bi bi-receipt"></i> Ventas
    </a>
    <a href="{{ route('reportes.productos') }}"
       class="nav-link {{ request()->routeIs('reportes.productos') ? 'active' : '' }}">
      <i class="bi bi-bar-chart"></i> Productos Más Vendidos
    </a>
    <a href="{{ route('reportes.mensual') }}"
       class="nav-link {{ request()->routeIs('reportes.mensual') ? 'active' : '' }}">
      <i class="bi bi-graph-up"></i> Gráfica Mensual
    </a>
    <a href="{{ route('reportes.cierres') }}"
       class="nav-link {{ request()->routeIs('reportes.cierres') ? 'active' : '' }}">
      <i class="bi bi-cash-stack"></i> Cierres de Caja
    </a>
  </div>

  <!-- Main content -->
  <main class="main-content">
    @if(session('success'))
      <div class="alert alert-success alert-dismissible fade show">
        {{ session('success') }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    @endif
    @yield('content')
  </main>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
  @yield('scripts')
</body>
</html>
