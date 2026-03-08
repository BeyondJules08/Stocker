<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Usuario extends Model
{
    protected $table = 'usuarios';
    public $timestamps = false;

    protected $fillable = [
        'nombre', 'email', 'password_hash', 'rol_id', 'activo', 'ultimo_acceso',
    ];

    protected $hidden = ['password_hash'];

    public function rol()
    {
        return $this->belongsTo(Rol::class, 'rol_id');
    }

    public function ventas()
    {
        return $this->hasMany(Venta::class, 'usuario_id');
    }

    public function cierres()
    {
        return $this->hasMany(CierreCaja::class, 'usuario_id');
    }
}
