<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('facturas')) return;
        Schema::create('facturas', function (Blueprint $table) {
            $table->id();
            $table->string('folio_fiscal', 36)->unique();
            $table->unsignedBigInteger('venta_id')->unique();
            $table->unsignedBigInteger('cliente_id');
            $table->string('xml_url', 500);
            $table->string('pdf_url', 500);
            $table->decimal('subtotal', 12, 2);
            $table->decimal('iva', 12, 2);
            $table->decimal('total', 12, 2);
            $table->timestamp('fecha_emision')->useCurrent();
            $table->foreign('venta_id')->references('id')->on('ventas');
            $table->foreign('cliente_id')->references('id')->on('clientes');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('facturas');
    }
};
