<?php

use App\Http\Controllers\Auth\LoginController;
use App\Http\Controllers\Reportes\ReportesController;
use Illuminate\Support\Facades\Route;

// Auth routes
Route::get('/login', [LoginController::class, 'showLogin'])->name('login');
Route::post('/login', [LoginController::class, 'login'])->name('login.post');
Route::post('/logout', [LoginController::class, 'logout'])->name('logout');

// Protected routes — gerentes only
Route::middleware(['auth', 'gerente'])->group(function () {
    Route::get('/', fn() => redirect()->route('reportes.index'));

    Route::prefix('reportes')->name('reportes.')->group(function () {
        Route::get('/',                     [ReportesController::class, 'index'])
             ->name('index');
        Route::get('/ventas',               [ReportesController::class, 'ventas'])
             ->name('ventas');
        Route::get('/exportar-ventas',      [ReportesController::class, 'exportarVentas'])
             ->name('exportar');
        Route::get('/productos-mas-vendidos', [ReportesController::class, 'productosMasVendidos'])
             ->name('productos');
        Route::get('/grafica-mensual',      [ReportesController::class, 'graficaMensual'])
             ->name('mensual');
        Route::get('/cierres-caja',         [ReportesController::class, 'cierresCaja'])
             ->name('cierres');
    });
});
