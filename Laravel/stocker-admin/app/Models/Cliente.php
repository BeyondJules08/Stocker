<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Cliente extends Model
{
    protected $table = 'clientes';
    public $timestamps = false;

    protected $fillable = [
        'razon_social', 'rfc', 'regimen_fiscal', 'uso_cfdi',
        'direccion_fiscal', 'codigo_postal', 'email', 'telefono', 'activo',
    ];

    public function ventas()
    {
        return $this->hasMany(Venta::class, 'cliente_id');
    }
}
