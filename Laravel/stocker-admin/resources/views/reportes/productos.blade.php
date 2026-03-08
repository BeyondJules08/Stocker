@extends('layouts.app')
@section('title', 'Productos Más Vendidos — Stocker')

@section('content')
<div class="page-header">
  <h2><i class="bi bi-bar-chart"></i> Productos Más Vendidos</h2>
</div>

<!-- Filtros -->
<div class="card mb-3">
  <div class="card-body">
    <form method="GET" action="{{ route('reportes.productos') }}" class="row g-2 align-items-end">
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

@if(count($chartLabels) > 0)
<div class="card mb-3">
  <div class="card-header bg-dark text-white">
    <i class="bi bi-trophy"></i> Top 10 Productos por Unidades Vendidas
  </div>
  <div class="card-body">
    <canvas id="chartProductos" height="120"></canvas>
  </div>
</div>
@endif

<div class="table-card">
  <table class="table table-hover align-middle">
    <thead>
      <tr>
        <th>#</th>
        <th>Producto</th>
        <th>Categoría</th>
        <th class="text-end">Unidades Vendidas</th>
        <th class="text-end">Ingresos Generados</th>
      </tr>
    </thead>
    <tbody>
      @forelse($productos as $i => $d)
      <tr>
        <td>
          @if($i === 0) <span class="badge bg-warning text-dark fs-6">🥇</span>
          @elseif($i === 1) <span class="badge bg-secondary fs-6">🥈</span>
          @elseif($i === 2) <span class="badge bg-danger fs-6">🥉</span>
          @else <span class="text-muted">{{ $i + 1 }}</span>
          @endif
        </td>
        <td class="fw-bold">{{ $d->producto?->nombre ?? 'N/A' }}</td>
        <td><span class="badge bg-secondary">{{ $d->producto?->categoria?->nombre ?? '—' }}</span></td>
        <td class="text-end fw-bold">{{ number_format($d->total_unidades) }}</td>
        <td class="text-end text-success fw-bold">${{ number_format($d->total_ingresos, 2) }}</td>
      </tr>
      @empty
      <tr>
        <td colspan="5" class="text-center text-muted py-4">
          <i class="bi bi-inbox fs-4"></i><br>Sin datos en el período.
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
new Chart(document.getElementById('chartProductos'), {
  type: 'bar',
  data: {
    labels: @json($chartLabels),
    datasets: [{
      label: 'Unidades vendidas',
      data: @json($chartData),
      backgroundColor: [
        'rgba(245,166,35,.85)', 'rgba(108,117,125,.85)', 'rgba(220,53,69,.85)',
        'rgba(13,202,240,.85)', 'rgba(25,135,84,.85)',
        'rgba(102,16,242,.85)', 'rgba(255,193,7,.85)', 'rgba(13,110,253,.85)',
        'rgba(214,51,132,.85)', 'rgba(32,201,151,.85)',
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
@endif
@endsection
