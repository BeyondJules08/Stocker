<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        // Gerente user for Laravel authentication (Panel de Reportes)
        User::firstOrCreate(
            ['email' => 'gerente@stocker.com'],
            [
                'name'     => 'Gerente Admin',
                'email'    => 'gerente@stocker.com',
                'password' => bcrypt('Admin123!'),
            ]
        );
    }
}
