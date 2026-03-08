<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stocker — Panel Gerencial</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <style>
    body { background: #0f0f23; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
    .login-card {
      background: #1a1a2e; border-radius: 16px; padding: 40px;
      width: 100%; max-width: 420px;
      box-shadow: 0 8px 32px rgba(0,0,0,.5);
    }
    .brand { font-size: 2rem; font-weight: 800; color: #f5a623; text-align: center; letter-spacing: 2px; }
    .brand-sub { color: rgba(255,255,255,.5); text-align: center; font-size: .9rem; margin-bottom: 28px; }
    .form-control { background: #16213e; border-color: #0f3460; color: #fff; }
    .form-control:focus { background: #16213e; border-color: #f5a623; color: #fff; box-shadow: 0 0 0 .2rem rgba(245,166,35,.25); }
    .form-label { color: rgba(255,255,255,.75); font-size: .85rem; }
    .btn-login { background: #f5a623; border: none; width: 100%; padding: 10px; font-size: 1rem; font-weight: 600; border-radius: 8px; color: #1a1a2e; }
    .btn-login:hover { background: #d4891a; }
    .badge-gerente {
      display: inline-block; background: rgba(245,166,35,.15);
      color: #f5a623; border: 1px solid #f5a623;
      border-radius: 20px; padding: 2px 12px; font-size: .75rem;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <div class="login-card">
    <div class="brand"><i class="bi bi-box-seam"></i> STOCKER</div>
    <p class="brand-sub">
      <span class="badge-gerente"><i class="bi bi-shield-check"></i> Panel Gerencial</span>
    </p>

    @if($errors->any())
      <div class="alert alert-danger py-2 text-center" style="font-size:.85rem">
        {{ $errors->first() }}
      </div>
    @endif

    <form method="POST" action="{{ route('login.post') }}">
      @csrf
      <div class="mb-3">
        <label class="form-label"><i class="bi bi-envelope"></i> Correo electrónico</label>
        <input type="email" name="email" class="form-control"
               value="{{ old('email') }}"
               placeholder="gerente@stocker.com" required autofocus>
      </div>
      <div class="mb-4">
        <label class="form-label"><i class="bi bi-lock"></i> Contraseña</label>
        <input type="password" name="password" class="form-control"
               placeholder="••••••••" required>
      </div>
      <button type="submit" class="btn btn-login">
        <i class="bi bi-box-arrow-in-right"></i> Acceder al Panel
      </button>
    </form>

    <div class="text-center mt-4" style="color:rgba(255,255,255,.3);font-size:.75rem">
      Stocker v1.0 &mdash; Sistema de Reportes
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
