<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('cierres_caja')) return;
        Schema::create('cierres_caja', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('usuario_id');
            $table->date('fecha');
            $table->decimal('total_ventas_efectivo', 12, 2);
            $table->decimal('total_ventas_tarjeta', 12, 2);
            $table->decimal('total_ventas', 12, 2);
            $table->integer('num_transacciones');
            $table->decimal('efectivo_contado', 12, 2);
            $table->decimal('diferencia', 12, 2);
            $table->text('nota')->nullable();
            $table->foreign('usuario_id')->references('id')->on('usuarios');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('cierres_caja');
    }
};
