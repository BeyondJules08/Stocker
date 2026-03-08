<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Proveedor extends Model
{
    protected $table = 'proveedores';
    public $timestamps = false;

    protected $fillable = ['nombre', 'rfc', 'telefono', 'email', 'direccion', 'activo'];

    public function entradas()
    {
        return $this->hasMany(EntradaInventario::class, 'proveedor_id');
    }
}
