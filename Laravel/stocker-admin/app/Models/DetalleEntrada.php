<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class DetalleEntrada extends Model
{
    protected $table = 'detalle_entrada';
    public $timestamps = false;

    protected $fillable = ['entrada_id', 'producto_id', 'cantidad', 'costo_unitario', 'subtotal'];

    public function producto()
    {
        return $this->belongsTo(Producto::class, 'producto_id');
    }
}
