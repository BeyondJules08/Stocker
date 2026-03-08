import json
import os
from datetime import date, datetime
from decimal import Decimal
from flask import (Blueprint, render_template, request, jsonify,
                   current_app, send_file, flash, redirect, url_for, abort)
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Venta, DetalleVenta, Producto, Cliente
from app.utils.pdf_generator import generar_ticket_pdf

ventas_bp = Blueprint('ventas', __name__)

IVA_TASA = Decimal('0.16')


def _require_operativo():
    if current_user.rol.nombre != 'operativo':
        abort(403)


def _generar_folio_venta():
    hoy = date.today().strftime('%Y%m%d')
    count = Venta.query.filter(
        func.date(Venta.fecha) == date.today()
    ).count()
    return f'VTA-{hoy}-{count + 1:04d}'


@ventas_bp.route('/')
@login_required
def index():
    _require_operativo()
    ventas = (Venta.query
              .filter(func.date(Venta.fecha) == date.today())
              .filter_by(usuario_id=current_user.id)
              .order_by(Venta.fecha.desc())
              .all())
    total_dia = sum(v.total for v in ventas)
    return render_template('ventas/index.html', ventas=ventas, total_dia=total_dia)


@ventas_bp.route('/nueva')
@login_required
def nueva():
    _require_operativo()
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.razon_social).all()
    return render_template('ventas/nueva.html', clientes=clientes)


@ventas_bp.route('/nueva', methods=['POST'])
@login_required
def procesar_venta():
    _require_operativo()
    data = request.get_json()
    if not data or not data.get('items'):
        return jsonify({'error': 'Sin artículos en la venta'}), 400

    items = data['items']
    metodo_pago = data.get('metodo_pago', 'Efectivo')
    monto_recibido = Decimal(str(data.get('monto_recibido', 0)))
    cliente_id = data.get('cliente_id') or None

    # Validate stock
    for item in items:
        prod = Producto.query.get(item['producto_id'])
        if not prod or not prod.activo:
            return jsonify({'error': f'Producto no válido: {item["producto_id"]}'}), 400
        if prod.stock_actual < item['cantidad']:
            return jsonify({'error': f'Stock insuficiente para {prod.nombre}'}), 400

    subtotal = Decimal('0')
    for item in items:
        subtotal += Decimal(str(item['precio_unitario'])) * item['cantidad']

    iva = (subtotal * IVA_TASA).quantize(Decimal('0.01'))
    total = subtotal + iva
    cambio = (monto_recibido - total) if metodo_pago == 'Efectivo' else Decimal('0')

    venta = Venta(
        folio=_generar_folio_venta(),
        usuario_id=current_user.id,
        cliente_id=cliente_id,
        subtotal=subtotal,
        iva=iva,
        total=total,
        metodo_pago=metodo_pago,
        monto_recibido=monto_recibido if metodo_pago == 'Efectivo' else None,
        cambio=cambio if metodo_pago == 'Efectivo' else None,
        estado='completada',
        facturada=False,
    )
    db.session.add(venta)
    db.session.flush()

    for item in items:
        prod = Producto.query.get(item['producto_id'])
        detalle = DetalleVenta(
            venta_id=venta.id,
            producto_id=prod.id,
            cantidad=item['cantidad'],
            precio_unitario=Decimal(str(item['precio_unitario'])),
            subtotal=Decimal(str(item['precio_unitario'])) * item['cantidad'],
        )
        prod.stock_actual -= item['cantidad']
        db.session.add(detalle)

    db.session.commit()

    ticket_url = url_for('ventas.ticket', venta_id=venta.id)
    return jsonify({
        'success': True,
        'venta_id': venta.id,
        'folio': venta.folio,
        'total': float(total),
        'cambio': float(cambio),
        'ticket_url': ticket_url,
    })


@ventas_bp.route('/<int:venta_id>/ticket')
@login_required
def ticket(venta_id):
    _require_operativo()
    venta = Venta.query.get_or_404(venta_id)
    detalles = venta.detalles

    pdf_dir = current_app.config['PDF_FOLDER']
    filename = f'ticket_{venta.folio}.pdf'
    pdf_path = os.path.join(pdf_dir, filename)

    if not os.path.exists(pdf_path):
        generar_ticket_pdf(venta, detalles, pdf_path)

    return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')


@ventas_bp.route('/buscar-producto')
@login_required
def buscar_producto():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    productos = (Producto.query
                 .filter(Producto.activo == True)
                 .filter(
                     (Producto.nombre.ilike(f'%{q}%')) |
                     (Producto.codigo_barras == q)
                 )
                 .limit(10)
                 .all())

    result = [{
        'id': p.id,
        'nombre': p.nombre,
        'codigo_barras': p.codigo_barras or '',
        'precio_venta': float(p.precio_venta),
        'stock_actual': p.stock_actual,
    } for p in productos]

    return jsonify(result)
