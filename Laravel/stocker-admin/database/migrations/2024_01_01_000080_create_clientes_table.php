<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('clientes')) return;
        Schema::create('clientes', function (Blueprint $table) {
            $table->id();
            $table->string('razon_social', 200);
            $table->string('rfc', 13)->unique();
            $table->string('regimen_fiscal', 100);
            $table->string('uso_cfdi', 10)->default('G03');
            $table->string('direccion_fiscal', 300);
            $table->string('codigo_postal', 5);
            $table->string('email', 150);
            $table->string('telefono', 20)->nullable();
            $table->boolean('activo')->default(true);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('clientes');
    }
};
