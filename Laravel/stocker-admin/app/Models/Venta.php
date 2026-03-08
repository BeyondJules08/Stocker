<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Venta extends Model
{
    protected $table = 'ventas';
    public $timestamps = false;

    protected $fillable = [
        'folio', 'usuario_id', 'cliente_id', 'subtotal', 'iva', 'total',
        'metodo_pago', 'monto_recibido', 'cambio', 'estado', 'facturada', 'fecha',
    ];

    protected $casts = [
        'fecha'     => 'datetime',
        'facturada' => 'boolean',
        'subtotal'  => 'decimal:2',
        'iva'       => 'decimal:2',
        'total'     => 'decimal:2',
    ];

    public function usuario()
    {
        return $this->belongsTo(Usuario::class, 'usuario_id');
    }

    public function cliente()
    {
        return $this->belongsTo(Cliente::class, 'cliente_id');
    }

    public function detalles()
    {
        return $this->hasMany(DetalleVenta::class, 'venta_id');
    }

    public function factura()
    {
        return $this->hasOne(Factura::class, 'venta_id');
    }
}
