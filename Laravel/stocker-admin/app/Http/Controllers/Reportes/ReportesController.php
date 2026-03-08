<?php

namespace App\Http\Controllers\Reportes;

use App\Http\Controllers\Controller;
use App\Models\CierreCaja;
use App\Models\DetalleVenta;
use App\Models\EntradaInventario;
use App\Models\Factura;
use App\Models\Producto;
use App\Models\Venta;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ReportesController extends Controller
{
    // ── Dashboard ─────────────────────────────────────────────────────────────

    public function index()
    {
        $now = now();
        $monthStart = $now->copy()->startOfMonth();
        $monthEnd = $now->copy()->endOfMonth();

        $totalVentasMes = Venta::whereBetween('fecha', [$monthStart, $monthEnd])
            ->where('estado', 'completada')
            ->sum('total');

        $numVentasMes = Venta::whereBetween('fecha', [$monthStart, $monthEnd])
            ->where('estado', 'completada')
            ->count();

        $facturasMes = Factura::whereBetween('fecha_emision', [$monthStart, $monthEnd])
            ->count();

        $productosStockBajo = Producto::whereRaw('stock_actual <= stock_minimo')
            ->where('activo', true)
            ->count();

        // Ventas últimos 7 días para la gráfica
        $labels7 = [];
        $data7 = [];
        for ($i = 6; $i >= 0; $i--) {
            $day = now()->subDays($i);
            $labels7[] = $day->format('d/m');
            $data7[] = (float) Venta::whereDate('fecha', $day->toDateString())
                ->where('estado', 'completada')
                ->sum('total');
        }

        // Top 5 productos del mes
        $top5 = DetalleVenta::select('producto_id',
                DB::raw('SUM(cantidad) as total_unidades'),
                DB::raw('SUM(subtotal) as total_ingresos'))
            ->whereHas('venta', fn($q) => $q->whereBetween('fecha', [$monthStart, $monthEnd])
                ->where('estado', 'completada'))
            ->groupBy('producto_id')
            ->orderByDesc('total_unidades')
            ->with('producto')
            ->limit(5)
            ->get();

        $top5Labels = $top5->map(fn($d) => $d->producto?->nombre ?? 'N/A')->toArray();
        $top5Data   = $top5->map(fn($d) => (int) $d->total_unidades)->toArray();

        return view('reportes.index', compact(
            'totalVentasMes', 'numVentasMes', 'facturasMes', 'productosStockBajo',
            'labels7', 'data7', 'top5Labels', 'top5Data'
        ));
    }

    // ── Ventas ────────────────────────────────────────────────────────────────

    public function ventas(Request $request)
    {
        $inicio = $request->input('fecha_inicio', now()->startOfMonth()->toDateString());
        $fin    = $request->input('fecha_fin', now()->toDateString());

        $ventas = Venta::with(['usuario', 'cliente'])
            ->whereBetween(DB::raw('DATE(fecha)'), [$inicio, $fin])
            ->where('estado', 'completada')
            ->orderByDesc('fecha')
            ->get();

        $resumen = [
            'num'      => $ventas->count(),
            'subtotal' => $ventas->sum('subtotal'),
            'iva'      => $ventas->sum('iva'),
            'total'    => $ventas->sum('total'),
        ];

        // Chart: daily totals
        $ventasPorDia = $ventas->groupBy(fn($v) => $v->fecha->format('d/m/Y'));
        $chartLabels = $ventasPorDia->keys()->toArray();
        $chartData   = $ventasPorDia->map(fn($g) => (float) $g->sum('total'))->values()->toArray();

        return view('reportes.ventas', compact(
            'ventas', 'resumen', 'inicio', 'fin', 'chartLabels', 'chartData'
        ));
    }

    // ── Productos más vendidos ─────────────────────────────────────────────────

    public function productosMasVendidos(Request $request)
    {
        $inicio = $request->input('fecha_inicio', now()->startOfMonth()->toDateString());
        $fin    = $request->input('fecha_fin', now()->toDateString());

        $productos = DetalleVenta::select(
                'producto_id',
                DB::raw('SUM(cantidad) as total_unidades'),
                DB::raw('SUM(subtotal) as total_ingresos')
            )
            ->whereHas('venta', function ($q) use ($inicio, $fin) {
                $q->whereBetween(DB::raw('DATE(fecha)'), [$inicio, $fin])
                  ->where('estado', 'completada');
            })
            ->groupBy('producto_id')
            ->orderByDesc('total_unidades')
            ->with('producto.categoria')
            ->limit(10)
            ->get();

        $chartLabels = $productos->map(fn($d) => $d->producto?->nombre ?? 'N/A')->toArray();
        $chartData   = $productos->map(fn($d) => (int) $d->total_unidades)->toArray();

        return view('reportes.productos', compact(
            'productos', 'inicio', 'fin', 'chartLabels', 'chartData'
        ));
    }

    // ── Gráfica mensual ventas vs gastos ──────────────────────────────────────

    public function graficaMensual()
    {
        $meses = [];
        $ventasMensuales = [];
        $gastosMensuales = [];
        $datos = [];

        for ($i = 11; $i >= 0; $i--) {
            $mes = now()->subMonths($i);
            $label = $mes->format('M Y');
            $inicio = $mes->copy()->startOfMonth();
            $fin    = $mes->copy()->endOfMonth();

            $ventas = (float) Venta::whereBetween('fecha', [$inicio, $fin])
                ->where('estado', 'completada')
                ->sum('total');

            $gastos = (float) EntradaInventario::whereBetween('fecha', [$inicio, $fin])
                ->sum('total');

            $meses[] = $label;
            $ventasMensuales[] = $ventas;
            $gastosMensuales[] = $gastos;
            $datos[] = [
                'mes'      => $label,
                'ventas'   => $ventas,
                'gastos'   => $gastos,
                'utilidad' => $ventas - $gastos,
            ];
        }

        return view('reportes.mensual', compact(
            'meses', 'ventasMensuales', 'gastosMensuales', 'datos'
        ));
    }

    // ── Cierres de caja ───────────────────────────────────────────────────────

    public function cierresCaja(Request $request)
    {
        $inicio = $request->input('fecha_inicio', now()->startOfMonth()->toDateString());
        $fin    = $request->input('fecha_fin', now()->toDateString());

        $cierres = CierreCaja::with('usuario')
            ->whereBetween('fecha', [$inicio, $fin])
            ->orderByDesc('fecha')
            ->get();

        return view('reportes.cierres', compact('cierres', 'inicio', 'fin'));
    }

    // ── Exportar ventas CSV ───────────────────────────────────────────────────

    public function exportarVentas(Request $request)
    {
        $inicio = $request->input('fecha_inicio', now()->startOfMonth()->toDateString());
        $fin    = $request->input('fecha_fin', now()->toDateString());

        $ventas = Venta::with(['usuario', 'cliente'])
            ->whereBetween(DB::raw('DATE(fecha)'), [$inicio, $fin])
            ->where('estado', 'completada')
            ->orderByDesc('fecha')
            ->get();

        $filename = "ventas_{$inicio}_{$fin}.csv";
        $headers = [
            'Content-Type'        => 'text/csv; charset=UTF-8',
            'Content-Disposition' => "attachment; filename=\"{$filename}\"",
        ];

        $callback = function () use ($ventas) {
            $handle = fopen('php://output', 'w');
            fprintf($handle, chr(0xEF).chr(0xBB).chr(0xBF)); // UTF-8 BOM

            fputcsv($handle, ['Folio', 'Fecha', 'Usuario', 'Cliente', 'Método Pago',
                              'Subtotal', 'IVA', 'Total', 'Facturada']);

            foreach ($ventas as $v) {
                fputcsv($handle, [
                    $v->folio,
                    $v->fecha->format('d/m/Y H:i'),
                    $v->usuario?->nombre ?? 'N/A',
                    $v->cliente?->razon_social ?? 'Público general',
                    $v->metodo_pago,
                    number_format($v->subtotal, 2),
                    number_format($v->iva, 2),
                    number_format($v->total, 2),
                    $v->facturada ? 'Sí' : 'No',
                ]);
            }
            fclose($handle);
        };

        return response()->stream($callback, 200, $headers);
    }
}
