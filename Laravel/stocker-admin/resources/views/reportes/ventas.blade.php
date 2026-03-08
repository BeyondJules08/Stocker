@extends('layouts.app')
@section('title', 'Reporte de Ventas — Stocker')

@section('content')
<div class="page-header">
  <h2><i class="bi bi-receipt"></i> Reporte de Ventas</h2>
  <a href="{{ route('reportes.exportar', ['fecha_inicio' => $inicio, 'fecha_fin' => $fin]) }}"
     class="btn btn-success">
    <i class="bi bi-file-earmark-spreadsheet"></i> Exportar CSV
  </a>
</div>

<!-- Filtros -->
<div class="card mb-3">
  <div class="card-body">
    <form method="GET" action="{{ route('reportes.ventas') }}" class="row g-2 align-items-end">
      <div class="col-md-4">
        <label class="form-label fw-bold small">Fecha inicio</label>
        <input type="date" name="fecha_inicio" class="form-control" value="{{ $inicio }}">
      </div>
      <div class="col-md-4">
        <label class="form-label fw-bold small">Fecha fin</label>
        <input type="date" name="fecha_fin" class="form-control" value="{{ $fin }}">
      </div>
      <div class="col-md-4">
        <button type="submit" class="btn btn-warning w-100">
          <i class="bi bi-funnel"></i> Filtrar
        </button>
      </div>
    </form>
  </div>
</div>

<!-- Resumen -->
<div class="row g-3 mb-3">
  <div class="col-md-3">
    <div class="stat-card">
      <div class="label">Ventas</div>
      <div class="value">{{ $resumen['num'] }}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="stat-card">
      <div class="label">Subtotal</div>
      <div class="value">${{ number_format($resumen['subtotal'], 2) }}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="stat-card">
      <div class="label">IVA</div>
      <div class="value">${{ number_format($resumen['iva'], 2) }}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="stat-card" style="border-color:#198754">
      <div class="label">Total</div>
      <div class="value text-success">${{ number_format($resumen['total'], 2) }}</div>
    </div>
  </div>
</div>

<!-- Gráfica ventas por día -->
@if(count($chartLabels) > 0)
<div class="card mb-3">
  <div class="card-header bg-dark text-white">
    <i class="bi bi-bar-chart"></i> Ventas por Día
  </div>
  <div class="card-body">
    <canvas id="ventasDia" height="80"></canvas>
  </div>
</div>
@endif

<!-- Tabla -->
<div class="table-card">
  <table class="table table-hover align-middle">
    <thead>
      <tr>
        <th>Folio</th>
        <th>Fecha</th>
        <th>Cajero</th>
        <th>Cliente</th>
        <th>Método</th>
        <th class="text-end">Total</th>
        <th>Facturada</th>
      </tr>
    </thead>
    <tbody>
      @forelse($ventas as $v)
      <tr>
        <td><code>{{ $v->folio }}</code></td>
        <td>{{ $v->fecha->format('d/m/Y H:i') }}</td>
        <td>{{ $v->usuario?->nombre ?? 'N/A' }}</td>
        <td>{{ $v->cliente?->razon_social ?? 'Público general' }}</td>
        <td>
          @if($v->metodo_pago === 'Efectivo')
            <span class="badge bg-success"><i class="bi bi-cash"></i> Efectivo</span>
          @else
            <span class="badge bg-primary"><i class="bi bi-credit-card"></i> Tarjeta</span>
          @endif
        </td>
        <td class="text-end fw-bold">${{ number_format($v->total, 2) }}</td>
        <td>
          @if($v->facturada)
            <span class="badge bg-info">Sí</span>
          @else
            <span class="badge bg-secondary">No</span>
          @endif
        </td>
      </tr>
      @empty
      <tr>
        <td colspan="7" class="text-center text-muted py-4">
          <i class="bi bi-inbox fs-4"></i><br>Sin ventas en el período.
        </td>
      </tr>
      @endforelse
    </tbody>
  </table>
</div>
@endsection

@section('scripts')
@if(count($chartLabels) > 0)
<script>
new Chart(document.getElementById('ventasDia'), {
  type: 'bar',
  data: {
    labels: @json($chartLabels),
    datasets: [{
      label: 'Ventas ($)',
      data: @json($chartData),
      backgroundColor: 'rgba(245,166,35,.7)',
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
</script>
@endif
@endsection
