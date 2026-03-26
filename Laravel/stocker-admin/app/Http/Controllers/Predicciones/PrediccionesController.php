<?php

namespace App\Http\Controllers\Predicciones;

use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\Http;

class PrediccionesController extends Controller
{
    public function index()
    {
        $flaskUrl = env('FLASK_URL', 'http://flask:5000');

        try {
            $response = Http::timeout(20)->get("{$flaskUrl}/api/ml/prediccion");

            if ($response->successful()) {
                $payload        = $response->json();
                $predicciones   = $payload['predicciones']    ?? [];
                $mae            = $payload['mae']             ?? null;
                $r2             = $payload['r2']              ?? null;
                $totalRegistros = $payload['total_registros'] ?? 0;
                $fuenteDatos    = $payload['fuente_datos']    ?? 'desconocida';
                $error          = null;
            } else {
                throw new \Exception('Flask respondió con estado HTTP ' . $response->status());
            }
        } catch (\Exception $e) {
            $predicciones   = [];
            $mae            = null;
            $r2             = null;
            $totalRegistros = 0;
            $fuenteDatos    = null;
            $error          = $e->getMessage();
        }

        return view('predicciones.index', compact(
            'predicciones', 'mae', 'r2', 'totalRegistros', 'fuenteDatos', 'error'
        ));
    }

    public function retrain()
    {
        $flaskUrl = env('FLASK_URL', 'http://flask:5000');

        try {
            $response = Http::timeout(130)->post("{$flaskUrl}/api/ml/retrain");

            if ($response->successful() && ($response->json()['ok'] ?? false)) {
                return redirect()->route('predicciones.index')
                    ->with('success', 'Modelo reentrenado correctamente.');
            }

            $msg = $response->json()['error'] ?? 'Error desconocido al reentrenar.';
            return redirect()->route('predicciones.index')->with('error', $msg);
        } catch (\Exception $e) {
            return redirect()->route('predicciones.index')
                ->with('error', 'No se pudo contactar el servicio ML: ' . $e->getMessage());
        }
    }
}
