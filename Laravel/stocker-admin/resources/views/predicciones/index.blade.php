@extends('layouts.app')

@section('title', 'Stocker — Pronóstico de Demanda')

@section('head')
<style>
  .metric-card {
    background: #fff; border-radius: 12px; padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
  }
  .metric-card .metric-value { font-size: 1.7rem; font-weight: 700; color: #1a1a2e; }
  .metric-card .metric-label { font-size: .82rem; color: #6c757d; margin-top: 2px; }
  .metric-card .metric-icon  { font-size: 2rem; }
  .chart-card {
    background: #fff; border-radius: 12px; padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
  }
  .chart-card h6 { color: #1a1a2e; font-weight: 700; margin-bottom: 14px; }
  .badge-cat { font-size: .75rem; padding: 3px 8px; border-radius: 20px; }
  .dias-ok      { color: #198754; font-weight: 600; }
  .dias-warning { color: #fd7e14; font-weight: 600; }
  .dias-danger  { color: #dc3545; font-weight: 600; }
</style>
@endsection

@section('content')
<div class="page-header d-flex align-items-center justify-content-between flex-wrap gap-2">
  <h2 class="mb-0">
    <i class="bi bi-cpu me-2"></i>Pronóstico de Demanda
    <small class="text-muted fs-6 fw-normal">Regresión Lineal Múltiple</small>
  </h2>

  @if(!$error)
  <form action="{{ route('predicciones.retrain') }}" method="POST">
    @csrf
    <button type="submit" class="btn btn-outline-primary btn-sm"
            onclick="return confirm('¿Reentrenar el modelo con los datos actuales?')">
      <i class="bi bi-arrow-clockwise me-1"></i>Reentrenar modelo
    </button>
  </form>
  @endif
</div>

{{-- Alertas de sesión --}}
@if(session('success'))
  <div class="alert alert-success alert-dismissible fade show mt-3" role="alert">
    <i class="bi bi-check-circle-fill me-2"></i>{{ session('success') }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>
@endif
@if(session('error'))
  <div class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
    <i class="bi bi-x-circle-fill me-2"></i>{{ session('error') }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>
@endif

{{-- Error del servicio ML --}}
@if($error)
  <div class="alert alert-warning d-flex align-items-center gap-2 mt-3">
    <i class="bi bi-exclamation-triangle-fill fs-5"></i>
    <div>
      <strong>Servicio ML no disponible:</strong> {{ $error }}<br>
      <small class="text-muted">Ejecuta <code>python train_model.py</code> dentro del contenedor Flask.</small>
    </div>
  </div>
@endif

{{-- Métricas del modelo --}}
@if(!$error)

@php
  $fuenteLabel = match($fuenteDatos) {
    'real'      => ['Datos reales',      'success',   'bi-database-check'],
    'mixta'     => ['Datos mixtos',      'warning',   'bi-database-gear'],
    'sintetica' => ['Datos sintéticos',  'secondary', 'bi-database-dash'],
    default     => ['Fuente desconocida','dark',      'bi-database'],
  };
@endphp

<div class="row g-3 mb-4 mt-1">
  <div class="col-md-3">
    <div class="metric-card d-flex align-items-center gap-3">
      <span class="metric-icon text-warning"><i class="bi bi-graph-up-arrow"></i></span>
      <div>
        <div class="metric-value">{{ $r2 !== null ? number_format($r2 * 100, 1).'%' : '—' }}</div>
        <div class="metric-label">R² — Varianza explicada</div>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="metric-card d-flex align-items-center gap-3">
      <span class="metric-icon text-primary"><i class="bi bi-rulers"></i></span>
      <div>
        <div class="metric-value">{{ $mae !== null ? '±'.number_format($mae, 1) : '—' }}</div>
        <div class="metric-label">MAE — Error promedio (uds.)</div>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="metric-card d-flex align-items-center gap-3">
      <span class="metric-icon text-success"><i class="bi bi-table"></i></span>
      <div>
        <div class="metric-value">{{ number_format($totalRegistros) }}</div>
        <div class="metric-label">Registros de entrenamiento</div>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="metric-card d-flex align-items-center gap-3">
      <span class="metric-icon text-{{ $fuenteLabel[1] }}"><i class="bi {{ $fuenteLabel[2] }}"></i></span>
      <div>
        <div class="metric-value" style="font-size:1.1rem">{{ $fuenteLabel[0] }}</div>
        <div class="metric-label">{{ count($predicciones) }} productos analizados</div>
      </div>
    </div>
  </div>
</div>

@if($fuenteDatos !== 'real')
<div class="alert alert-info d-flex align-items-center gap-2 mb-3">
  <i class="bi bi-info-circle-fill"></i>
  <span>
    El modelo usa datos <strong>{{ $fuenteDatos === 'mixta' ? 'parcialmente sintéticos' : 'sintéticos' }}</strong>
    basados en tu catálogo real.
    A medida que registres ventas, usa <strong>Reentrenar modelo</strong> para mejorar la precisión.
  </span>
</div>
@endif

{{-- Gráfica --}}
@if(count($predicciones) > 0)
<div class="row g-3 mb-4">
  <div class="col-12">
    <div class="chart-card">
      <h6><i class="bi bi-bar-chart-fill me-2 text-warning"></i>Demanda Diaria Predicha por Producto</h6>
      <canvas id="chartPrediccion" height="90"></canvas>
    </div>
  </div>
</div>

{{-- Tabla de predicciones --}}
<div class="table-card">
  <div class="p-3 border-bottom d-flex align-items-center justify-content-between">
    <h6 class="mb-0 fw-bold"><i class="bi bi-list-ul me-2"></i>Detalle por Producto</h6>
    <span class="badge bg-secondary">Ordenado por mayor demanda predicha</span>
  </div>
  <table class="table table-hover mb-0">
    <thead>
      <tr>
        <th>#</th>
        <th>Producto</th>
        <th>Categoría</th>
        <th class="text-end">Precio</th>
        <th class="text-end">Stock actual</th>
        <th class="text-end">Stock mínimo</th>
        <th class="text-end">Uds. predichas/día</th>
        <th class="text-end">Días de cobertura</th>
        <th class="text-center">Estado</th>
      </tr>
    </thead>
    <tbody>
      @foreach($predicciones as $i => $p)
      @php
        $dias   = $p['dias_cobertura'];
        $pred   = $p['prediccion_diaria'];
        $stock  = $p['nivel_inventario'];
        $minimo = $p['stock_minimo'];

        $critico  = $dias < 3  || $stock < $minimo;
        $advertir = !$critico && ($dias < 7 || $stock < $minimo * 1.5);
      @endphp
      <tr class="{{ $critico ? 'table-danger' : ($advertir ? 'table-warning' : '') }}">
        <td class="text-muted small">{{ $i + 1 }}</td>
        <td class="fw-semibold">{{ $p['producto'] }}</td>
        <td>
          @php
            $colores = [
              'Bebidas'     => 'primary',
              'Snacks'      => 'warning',
              'Lácteos'     => 'info',
              'Abarrotes'   => 'success',
              'Limpieza'    => 'secondary',
              'Higiene'     => 'danger',
              'Electrónica' => 'dark',
            ];
            $color = $colores[$p['categoria']] ?? 'dark';
          @endphp
          <span class="badge bg-{{ $color }} badge-cat">{{ $p['categoria'] }}</span>
        </td>
        <td class="text-end">${{ number_format($p['precio'], 2) }}</td>
        <td class="text-end">{{ number_format($stock) }}</td>
        <td class="text-end text-muted">{{ number_format($minimo) }}</td>
        <td class="text-end fw-bold">{{ number_format($pred) }}</td>
        <td class="text-end">
          @if($dias >= 999)
            <span class="text-muted">—</span>
          @else
            <span class="{{ $critico ? 'dias-danger' : ($advertir ? 'dias-warning' : 'dias-ok') }}">
              {{ number_format($dias, 1) }} días
            </span>
          @endif
        </td>
        <td class="text-center">
          @if($critico)
            <span class="badge bg-danger"><i class="bi bi-exclamation-triangle-fill"></i> Urgente</span>
          @elseif($advertir)
            <span class="badge bg-warning text-dark"><i class="bi bi-exclamation-circle-fill"></i> Reabastecer</span>
          @else
            <span class="badge bg-success"><i class="bi bi-check-circle-fill"></i> OK</span>
          @endif
        </td>
      </tr>
      @endforeach
    </tbody>
  </table>
</div>
@endif
@endif
@endsection

@section('scripts')
@if(!$error && count($predicciones) > 0)
<script>
(function () {
  const predicciones = @json($predicciones);
  const labels     = predicciones.map(p => p.producto);
  const valores    = predicciones.map(p => p.prediccion_diaria);
  const coberturas = predicciones.map(p => p.dias_cobertura >= 999 ? null : p.dias_cobertura);

  const catColors = {
    'Bebidas':     '#0d6efd',
    'Snacks':      '#ffc107',
    'Lácteos':     '#0dcaf0',
    'Abarrotes':   '#198754',
    'Limpieza':    '#6c757d',
    'Higiene':     '#dc3545',
    'Electrónica': '#212529',
  };
  const colors = predicciones.map(p => catColors[p.categoria] ?? '#1a1a2e');

  new Chart(document.getElementById('chartPrediccion'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Unidades predichas/día',
          data: valores,
          backgroundColor: colors,
          borderRadius: 6,
          order: 1,
        },
        {
          label: 'Días de cobertura',
          data: coberturas,
          type: 'line',
          borderColor: '#f5a623',
          backgroundColor: 'rgba(245,166,35,.15)',
          borderWidth: 2,
          pointRadius: 4,
          tension: 0.3,
          yAxisID: 'y2',
          order: 0,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: ctx => {
              if (ctx.dataset.label === 'Días de cobertura') {
                return ` Cobertura: ${ctx.parsed.y} días`;
              }
              return ` ${ctx.dataset.label}: ${ctx.parsed.y} uds.`;
            },
          },
        },
      },
      scales: {
        y:  { beginAtZero: true, title: { display: true, text: 'Unidades / día' } },
        y2: {
          beginAtZero: true,
          position: 'right',
          title: { display: true, text: 'Días de cobertura' },
          grid: { drawOnChartArea: false },
        },
        x: { ticks: { maxRotation: 30 } },
      },
    },
  });
})();
</script>
@endif
@endsection
