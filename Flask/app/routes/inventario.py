from datetime import date, datetime
from decimal import Decimal
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort)
from flask_login import login_required, current_user
from app import db
from app.models import (Producto, Categoria, Proveedor,
                        EntradaInventario, DetalleEntrada)

inventario_bp = Blueprint('inventario', __name__)


def _require_almacen():
    if current_user.rol.nombre != 'almacen':
        abort(403)


def _generar_folio_entrada():
    hoy = date.today().strftime('%Y%m%d')
    count = EntradaInventario.query.filter(
        EntradaInventario.fecha >= datetime.combine(date.today(), datetime.min.time())
    ).count()
    return f'ENT-{hoy}-{count + 1:04d}'


# ── Dashboard ────────────────────────────────────────────────────────────────

@inventario_bp.route('/')
@login_required
def dashboard():
    _require_almacen()
    productos_bajos = (Producto.query
                       .filter(Producto.activo == True)
                       .filter(Producto.stock_actual <= Producto.stock_minimo)
                       .order_by(Producto.stock_actual)
                       .all())
    total_productos = Producto.query.filter_by(activo=True).count()
    total_categorias = Categoria.query.filter_by(activo=True).count()
    total_proveedores = Proveedor.query.filter_by(activo=True).count()
    return render_template('inventario/dashboard.html',
                           productos_bajos=productos_bajos,
                           total_productos=total_productos,
                           total_categorias=total_categorias,
                           total_proveedores=total_proveedores)


# ── Productos ─────────────────────────────────────────────────────────────────

@inventario_bp.route('/productos')
@login_required
def productos():
    _require_almacen()
    items = (Producto.query
             .filter_by(activo=True)
             .order_by(Producto.nombre)
             .all())
    return render_template('inventario/productos.html', productos=items)


@inventario_bp.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def producto_nuevo():
    _require_almacen()
    categorias = Categoria.query.filter_by(activo=True).all()
    if request.method == 'POST':
        prod = Producto(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion'),
            codigo_barras=request.form.get('codigo_barras') or None,
            precio_compra=Decimal(request.form['precio_compra']),
            precio_venta=Decimal(request.form['precio_venta']),
            stock_actual=int(request.form.get('stock_actual', 0)),
            stock_minimo=int(request.form.get('stock_minimo', 5)),
            categoria_id=int(request.form['categoria_id']),
            activo=True,
        )
        db.session.add(prod)
        db.session.commit()
        flash('Producto creado correctamente.', 'success')
        return redirect(url_for('inventario.productos'))
    return render_template('inventario/producto_form.html',
                           categorias=categorias, producto=None)


@inventario_bp.route('/productos/<int:pid>/editar', methods=['GET', 'POST'])
@login_required
def producto_editar(pid):
    _require_almacen()
    prod = Producto.query.get_or_404(pid)
    categorias = Categoria.query.filter_by(activo=True).all()
    if request.method == 'POST':
        prod.nombre = request.form['nombre']
        prod.descripcion = request.form.get('descripcion')
        prod.codigo_barras = request.form.get('codigo_barras') or None
        prod.precio_compra = Decimal(request.form['precio_compra'])
        prod.precio_venta = Decimal(request.form['precio_venta'])
        prod.stock_actual = int(request.form.get('stock_actual', prod.stock_actual))
        prod.stock_minimo = int(request.form.get('stock_minimo', prod.stock_minimo))
        prod.categoria_id = int(request.form['categoria_id'])
        db.session.commit()
        flash('Producto actualizado.', 'success')
        return redirect(url_for('inventario.productos'))
    return render_template('inventario/producto_form.html',
                           categorias=categorias, producto=prod)


@inventario_bp.route('/productos/<int:pid>/eliminar', methods=['POST'])
@login_required
def producto_eliminar(pid):
    _require_almacen()
    prod = Producto.query.get_or_404(pid)
    prod.activo = False
    db.session.commit()
    flash('Producto desactivado.', 'info')
    return redirect(url_for('inventario.productos'))


# ── Categorías ────────────────────────────────────────────────────────────────

@inventario_bp.route('/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    _require_almacen()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if nombre:
            cat = Categoria(nombre=nombre,
                            descripcion=request.form.get('descripcion'))
            db.session.add(cat)
            db.session.commit()
            flash('Categoría creada.', 'success')
        return redirect(url_for('inventario.categorias'))
    cats = Categoria.query.filter_by(activo=True).all()
    return render_template('inventario/categorias.html', categorias=cats)


@inventario_bp.route('/categorias/<int:cid>/eliminar', methods=['POST'])
@login_required
def categoria_eliminar(cid):
    _require_almacen()
    cat = Categoria.query.get_or_404(cid)
    cat.activo = False
    db.session.commit()
    flash('Categoría desactivada.', 'info')
    return redirect(url_for('inventario.categorias'))


# ── Proveedores ───────────────────────────────────────────────────────────────

@inventario_bp.route('/proveedores')
@login_required
def proveedores():
    _require_almacen()
    items = Proveedor.query.filter_by(activo=True).order_by(Proveedor.nombre).all()
    return render_template('inventario/proveedores.html', proveedores=items)


@inventario_bp.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def proveedor_nuevo():
    _require_almacen()
    if request.method == 'POST':
        prov = Proveedor(
            nombre=request.form['nombre'],
            rfc=request.form['rfc'].upper(),
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            direccion=request.form.get('direccion'),
        )
        db.session.add(prov)
        db.session.commit()
        flash('Proveedor creado.', 'success')
        return redirect(url_for('inventario.proveedores'))
    return render_template('inventario/proveedor_form.html', proveedor=None)


@inventario_bp.route('/proveedores/<int:pid>/editar', methods=['GET', 'POST'])
@login_required
def proveedor_editar(pid):
    _require_almacen()
    prov = Proveedor.query.get_or_404(pid)
    if request.method == 'POST':
        prov.nombre = request.form['nombre']
        prov.rfc = request.form['rfc'].upper()
        prov.telefono = request.form.get('telefono')
        prov.email = request.form.get('email')
        prov.direccion = request.form.get('direccion')
        db.session.commit()
        flash('Proveedor actualizado.', 'success')
        return redirect(url_for('inventario.proveedores'))
    return render_template('inventario/proveedor_form.html', proveedor=prov)


# ── Entradas de inventario ────────────────────────────────────────────────────

@inventario_bp.route('/entradas')
@login_required
def entradas():
    _require_almacen()
    items = (EntradaInventario.query
             .order_by(EntradaInventario.fecha.desc())
             .all())
    return render_template('inventario/entradas.html', entradas=items)


@inventario_bp.route('/entradas/nueva', methods=['GET', 'POST'])
@login_required
def entrada_nueva():
    _require_almacen()
    proveedores = Proveedor.query.filter_by(activo=True).all()
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()

    if request.method == 'POST':
        proveedor_id = int(request.form['proveedor_id'])
        observaciones = request.form.get('observaciones')

        productos_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        costos = request.form.getlist('costo_unitario[]')

        if not productos_ids:
            flash('Agrega al menos un producto.', 'danger')
            return render_template('inventario/entrada_form.html',
                                   proveedores=proveedores, productos=productos)

        entrada = EntradaInventario(
            folio=_generar_folio_entrada(),
            proveedor_id=proveedor_id,
            usuario_id=current_user.id,
            total=Decimal('0'),
            observaciones=observaciones,
        )
        db.session.add(entrada)
        db.session.flush()

        total = Decimal('0')
        for pid, qty, costo in zip(productos_ids, cantidades, costos):
            pid = int(pid)
            qty = int(qty)
            costo_u = Decimal(costo)
            subtotal = costo_u * qty
            total += subtotal

            det = DetalleEntrada(
                entrada_id=entrada.id,
                producto_id=pid,
                cantidad=qty,
                costo_unitario=costo_u,
                subtotal=subtotal,
            )
            db.session.add(det)

            prod = Producto.query.get(pid)
            if prod:
                prod.stock_actual += qty

        entrada.total = total
        db.session.commit()
        flash(f'Entrada {entrada.folio} registrada correctamente.', 'success')
        return redirect(url_for('inventario.entradas'))

    return render_template('inventario/entrada_form.html',
                           proveedores=proveedores, productos=productos)
