<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Factura extends Model
{
    protected $table = 'facturas';
    public $timestamps = false;

    protected $fillable = [
        'folio_fiscal', 'venta_id', 'cliente_id', 'xml_url', 'pdf_url',
        'subtotal', 'iva', 'total', 'fecha_emision',
    ];

    protected $casts = [
        'fecha_emision' => 'datetime',
        'subtotal'      => 'decimal:2',
        'iva'           => 'decimal:2',
        'total'         => 'decimal:2',
    ];

    public function venta()
    {
        return $this->belongsTo(Venta::class, 'venta_id');
    }

    public function cliente()
    {
        return $this->belongsTo(Cliente::class, 'cliente_id');
    }
}
