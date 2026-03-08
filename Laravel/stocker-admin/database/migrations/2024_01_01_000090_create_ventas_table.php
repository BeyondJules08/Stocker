<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('ventas')) return;
        Schema::create('ventas', function (Blueprint $table) {
            $table->id();
            $table->string('folio', 20)->unique();
            $table->unsignedBigInteger('usuario_id');
            $table->unsignedBigInteger('cliente_id')->nullable();
            $table->decimal('subtotal', 12, 2);
            $table->decimal('iva', 12, 2);
            $table->decimal('total', 12, 2);
            $table->string('metodo_pago', 20);
            $table->decimal('monto_recibido', 12, 2)->nullable();
            $table->decimal('cambio', 12, 2)->nullable();
            $table->string('estado', 20)->default('completada');
            $table->boolean('facturada')->default(false);
            $table->timestamp('fecha')->useCurrent();
            $table->foreign('usuario_id')->references('id')->on('usuarios');
            $table->foreign('cliente_id')->references('id')->on('clientes');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('ventas');
    }
};
