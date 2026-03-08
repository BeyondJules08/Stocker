<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CierreCaja extends Model
{
    protected $table = 'cierres_caja';
    public $timestamps = false;

    protected $fillable = [
        'usuario_id', 'fecha', 'total_ventas_efectivo', 'total_ventas_tarjeta',
        'total_ventas', 'num_transacciones', 'efectivo_contado', 'diferencia', 'nota',
    ];

    protected $casts = [
        'fecha'                 => 'date',
        'total_ventas_efectivo' => 'decimal:2',
        'total_ventas_tarjeta'  => 'decimal:2',
        'total_ventas'          => 'decimal:2',
        'efectivo_contado'      => 'decimal:2',
        'diferencia'            => 'decimal:2',
    ];

    public function usuario()
    {
        return $this->belongsTo(Usuario::class, 'usuario_id');
    }
}
