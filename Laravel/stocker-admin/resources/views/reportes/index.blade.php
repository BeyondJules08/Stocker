@extends('layouts.app')
@section('title', 'Dashboard — Stocker Reportes')

@section('content')
<div class="page-header">
  <h2><i class="bi bi-speedometer2"></i> Dashboard Gerencial</h2>
  <span class="text-muted small">{{ now()->format('d/m/Y') }}</span>
</div>

<div class="row g-3 mb-4">
  <div class="col-md-3">
    <div class="stat-card">
      <div class="label"><i class="bi bi-currency-dollar"></i> Ventas del Mes</div>
      <div class="value">${{ number_format($totalVentasMes, 2) }}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="stat-card">
      <div class="label"><i class="bi bi-receipt"></i> Número de Ventas</div>
      <div class="value">{{ $numVentasMes }}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="stat-card" style="border-color:#0dcaf0">
      <div class="label"><i class="bi bi-file-earmark-text"></i> Facturas del Mes</div>
      <div class="value text-info">{{ $facturasMes }}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="stat-card" style="border-color:#dc3545">
      <div class="label"><i class="bi bi-exclamation-triangle"></i> Stock Bajo</div>
      <div class="value text-danger">{{ $productosStockBajo }}</div>
    </div>
  </div>
</div>

<div class="row g-3">
  <div class="col-md-7">
    <div class="card">
      <div class="card-header bg-dark text-white">
        <i class="bi bi-bar-chart"></i> Ventas Últimos 7 Días
      </div>
      <div class="card-body">
        <canvas id="chart7dias" height="120"></canvas>
      </div>
    </div>
  </div>
  <div class="col-md-5">
    <div class="card">
      <div class="card-header bg-dark text-white">
        <i class="bi bi-trophy"></i> Top 5 Productos del Mes
      </div>
      <div class="card-body">
        <canvas id="chartTop5" height="120"></canvas>
      </div>
    </div>
  </div>
</div>

<div class="mt-3 d-flex gap-2">
  <a href="{{ route('reportes.ventas') }}" class="btn btn-outline-warning">
    <i class="bi bi-receipt"></i> Ver Reporte de Ventas
  </a>
  <a href="{{ route('reportes.mensual') }}" class="btn btn-outline-warning">
    <i class="bi bi-graph-up"></i> Gráfica Mensual
  </a>
  <a href="{{ route('reportes.cierres') }}" class="btn btn-outline-warning">
    <i class="bi bi-cash-stack"></i> Cierres de Caja
  </a>
</div>
@endsection

@section('scripts')
<script>
new Chart(document.getElementById('chart7dias'), {
  type: 'bar',
  data: {
    labels: @json($labels7),
    datasets: [{
      label: 'Ventas ($)',
      data: @json($data7),
      backgroundColor: 'rgba(245, 166, 35, 0.7)',
      borderColor: '#f5a623',
      borderWidth: 1,
      borderRadius: 4,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, ticks: { callback: v => '$' + v.toLocaleString() } } }
  }
});

new Chart(document.getElementById('chartTop5'), {
  type: 'bar',
  data: {
    labels: @json($top5Labels),
    datasets: [{
      label: 'Unidades',
      data: @json($top5Data),
      backgroundColor: [
        'rgba(233,69,96,.8)', 'rgba(245,166,35,.8)', 'rgba(13,202,240,.8)',
        'rgba(25,135,84,.8)', 'rgba(108,117,125,.8)'
      ],
      borderRadius: 4,
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: { beginAtZero: true } }
  }
});
</script>
@endsection
