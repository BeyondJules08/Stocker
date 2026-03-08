@extends('layouts.app')
@section('title', 'Gráfica Mensual — Stocker')

@section('content')
<div class="page-header">
  <h2><i class="bi bi-graph-up"></i> Ventas vs Gastos — Últimos 12 Meses</h2>
</div>

<div class="card mb-4">
  <div class="card-header bg-dark text-white">
    <i class="bi bi-bar-chart-line"></i> Ventas vs Gastos (Entradas de Inventario)
  </div>
  <div class="card-body">
    <canvas id="chartMensual" height="100"></canvas>
  </div>
</div>

<div class="table-card">
  <table class="table table-hover align-middle">
    <thead>
      <tr>
        <th>Mes</th>
        <th class="text-end text-warning">Ventas</th>
        <th class="text-end text-danger">Gastos</th>
        <th class="text-end text-success">Utilidad Bruta</th>
        <th>Margen</th>
      </tr>
    </thead>
    <tbody>
      @foreach($datos as $d)
      <tr>
        <td class="fw-bold">{{ $d['mes'] }}</td>
        <td class="text-end">${{ number_format($d['ventas'], 2) }}</td>
        <td class="text-end text-danger">${{ number_format($d['gastos'], 2) }}</td>
        <td class="text-end fw-bold {{ $d['utilidad'] >= 0 ? 'text-success' : 'text-danger' }}">
          ${{ number_format($d['utilidad'], 2) }}
        </td>
        <td>
          @if($d['ventas'] > 0)
            @php $margen = ($d['utilidad'] / $d['ventas']) * 100; @endphp
            <div class="progress" style="height:18px;width:120px">
              <div class="progress-bar {{ $margen >= 0 ? 'bg-success' : 'bg-danger' }}"
                   style="width:{{ min(abs($margen), 100) }}%">
                {{ number_format($margen, 1) }}%
              </div>
            </div>
          @else
            <span class="text-muted">—</span>
          @endif
        </td>
      </tr>
      @endforeach
    </tbody>
  </table>
</div>
@endsection

@section('scripts')
<script>
new Chart(document.getElementById('chartMensual'), {
  type: 'line',
  data: {
    labels: @json($meses),
    datasets: [
      {
        label: 'Ventas',
        data: @json($ventasMensuales),
        borderColor: '#f5a623',
        backgroundColor: 'rgba(245,166,35,.1)',
        tension: 0.3,
        fill: true,
        pointRadius: 4,
      },
      {
        label: 'Gastos',
        data: @json($gastosMensuales),
        borderColor: '#dc3545',
        backgroundColor: 'rgba(220,53,69,.1)',
        tension: 0.3,
        fill: true,
        pointRadius: 4,
      }
    ]
  },
  options: {
    responsive: true,
    interaction: { intersect: false, mode: 'index' },
    plugins: {
      legend: { position: 'top' },
      tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: $${ctx.parsed.y.toLocaleString('es-MX', {minimumFractionDigits:2})}` } }
    },
    scales: {
      y: { beginAtZero: true, ticks: { callback: v => '$' + v.toLocaleString() } }
    }
  }
});
</script>
@endsection
