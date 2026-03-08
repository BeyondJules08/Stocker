@extends('layouts.app')
@section('title', 'Cierres de Caja — Stocker')

@section('content')
<div class="page-header">
  <h2><i class="bi bi-cash-stack"></i> Historial de Cierres de Caja</h2>
</div>

<!-- Filtros -->
<div class="card mb-3">
  <div class="card-body">
    <form method="GET" action="{{ route('reportes.cierres') }}" class="row g-2 align-items-end">
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

<!-- Resumen rápido -->
@if($cierres->isNotEmpty())
<div class="row g-3 mb-3">
  <div class="col-md-3">
    <div class="stat-card">
      <div class="label">Total Cierres</div>
      <div class="value">{{ $cierres->count() }}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="stat-card">
      <div class="label">Total Ventas</div>
      <div class="value">${{ number_format($cierres->sum('total_ventas'), 2) }}</div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="stat-card" style="border-color:#198754">
      <div class="label">Efectivo Recaudado</div>
      <div class="value text-success">${{ number_format($cierres->sum('total_ventas_efectivo'), 2) }}</div>
    </div>
  </div>
  <div class="col-md-3">
    @php $difTotal = $cierres->sum('diferencia'); @endphp
    <div class="stat-card" style="border-color:{{ $difTotal < 0 ? '#dc3545' : ($difTotal > 0 ? '#ffc107' : '#198754') }}">
      <div class="label">Diferencia Acumulada</div>
      <div class="value {{ $difTotal < 0 ? 'text-danger' : ($difTotal > 0 ? 'text-warning' : 'text-success') }}">
        ${{ number_format($difTotal, 2) }}
      </div>
    </div>
  </div>
</div>
@endif

<div class="table-card">
  <table class="table table-hover align-middle">
    <thead>
      <tr>
        <th>Fecha</th>
        <th>Cajero</th>
        <th class="text-end">Efectivo</th>
        <th class="text-end">Tarjeta</th>
        <th class="text-end">Total Ventas</th>
        <th class="text-end">Efectivo Contado</th>
        <th class="text-end">Diferencia</th>
        <th class="text-center"># Tx</th>
        <th>Nota</th>
      </tr>
    </thead>
    <tbody>
      @forelse($cierres as $c)
      <tr>
        <td class="fw-bold">{{ \Carbon\Carbon::parse($c->fecha)->format('d/m/Y') }}</td>
        <td>{{ $c->usuario?->nombre ?? 'N/A' }}</td>
        <td class="text-end">${{ number_format($c->total_ventas_efectivo, 2) }}</td>
        <td class="text-end">${{ number_format($c->total_ventas_tarjeta, 2) }}</td>
        <td class="text-end fw-bold">${{ number_format($c->total_ventas, 2) }}</td>
        <td class="text-end">${{ number_format($c->efectivo_contado, 2) }}</td>
        <td class="text-end fw-bold
          {{ $c->diferencia == 0 ? 'text-success' : ($c->diferencia < 0 ? 'text-danger' : 'text-warning') }}">
          ${{ number_format($c->diferencia, 2) }}
          @if($c->diferencia == 0) <i class="bi bi-check-circle-fill"></i>
          @elseif($c->diferencia < 0) <i class="bi bi-arrow-down-circle-fill"></i>
          @else <i class="bi bi-arrow-up-circle-fill"></i>
          @endif
        </td>
        <td class="text-center"><span class="badge bg-secondary">{{ $c->num_transacciones }}</span></td>
        <td class="text-muted small">{{ Str::limit($c->nota ?? '—', 40) }}</td>
      </tr>
      @empty
      <tr>
        <td colspan="9" class="text-center text-muted py-4">
          <i class="bi bi-inbox fs-4"></i><br>No hay cierres en el período.
        </td>
      </tr>
      @endforelse
    </tbody>
  </table>
</div>
@endsection
