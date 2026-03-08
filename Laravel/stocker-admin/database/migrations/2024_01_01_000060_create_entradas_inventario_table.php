<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('entradas_inventario')) return;
        Schema::create('entradas_inventario', function (Blueprint $table) {
            $table->id();
            $table->string('folio', 20)->unique();
            $table->unsignedBigInteger('proveedor_id');
            $table->unsignedBigInteger('usuario_id');
            $table->decimal('total', 12, 2);
            $table->text('observaciones')->nullable();
            $table->timestamp('fecha')->useCurrent();
            $table->foreign('proveedor_id')->references('id')->on('proveedores');
            $table->foreign('usuario_id')->references('id')->on('usuarios');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('entradas_inventario');
    }
};
