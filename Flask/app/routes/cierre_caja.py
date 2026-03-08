import json
from datetime import date, timedelta
from decimal import Decimal
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import CierreCaja, Venta

cierre_bp = Blueprint('cierre', __name__)


def _require_operativo():
    if current_user.rol.nombre != 'operativo':
        abort(403)


@cierre_bp.route('/')
@login_required
def index():
    _require_operativo()
    cierres = (CierreCaja.query
               .order_by(CierreCaja.fecha.desc())
               .limit(30)
               .all())

    # Chart data: last 7 days totals
    today = date.today()
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        total = db.session.query(func.coalesce(func.sum(Venta.total), 0)).filter(
            func.date(Venta.fecha) == day,
            Venta.estado == 'completada'
        ).scalar()
        chart_labels.append(day.strftime('%d/%m'))
        chart_data.append(float(total))

    return render_template('cierre_caja/index.html',
                           cierres=cierres,
                           chart_labels=json.dumps(chart_labels),
                           chart_data=json.dumps(chart_data))


@cierre_bp.route('/nuevo', methods=['GET'])
@login_required
def nuevo():
    _require_operativo()
    hoy = date.today()

    # Check if already closed today
    existente = CierreCaja.query.filter_by(
        usuario_id=current_user.id, fecha=hoy
    ).first()
    if existente:
        flash('Ya realizaste el cierre de caja de hoy.', 'warning')
        return redirect(url_for('cierre.index'))

    ventas_hoy = Venta.query.filter(
        func.date(Venta.fecha) == hoy,
        Venta.estado == 'completada'
    ).all()

    efectivo = sum(v.total for v in ventas_hoy if v.metodo_pago == 'Efectivo')
    tarjeta = sum(v.total for v in ventas_hoy if v.metodo_pago == 'Tarjeta')
    total = sum(v.total for v in ventas_hoy)
    num_tx = len(ventas_hoy)

    return render_template('cierre_caja/nuevo.html',
                           hoy=hoy,
                           total_efectivo=float(efectivo),
                           total_tarjeta=float(tarjeta),
                           total_ventas=float(total),
                           num_transacciones=num_tx)


@cierre_bp.route('/nuevo', methods=['POST'])
@login_required
def procesar_cierre():
    _require_operativo()
    hoy = date.today()

    existente = CierreCaja.query.filter_by(
        usuario_id=current_user.id, fecha=hoy
    ).first()
    if existente:
        flash('Ya realizaste el cierre de caja de hoy.', 'warning')
        return redirect(url_for('cierre.index'))

    ventas_hoy = Venta.query.filter(
        func.date(Venta.fecha) == hoy,
        Venta.estado == 'completada'
    ).all()

    efectivo = Decimal(str(sum(v.total for v in ventas_hoy if v.metodo_pago == 'Efectivo')))
    tarjeta = Decimal(str(sum(v.total for v in ventas_hoy if v.metodo_pago == 'Tarjeta')))
    total_ventas = efectivo + tarjeta
    num_tx = len(ventas_hoy)

    efectivo_contado = Decimal(request.form.get('efectivo_contado', '0'))
    nota = request.form.get('nota', '')
    diferencia = efectivo_contado - efectivo

    cierre = CierreCaja(
        usuario_id=current_user.id,
        fecha=hoy,
        total_ventas_efectivo=efectivo,
        total_ventas_tarjeta=tarjeta,
        total_ventas=total_ventas,
        num_transacciones=num_tx,
        efectivo_contado=efectivo_contado,
        diferencia=diferencia,
        nota=nota,
    )
    db.session.add(cierre)
    db.session.commit()

    flash('Cierre de caja registrado correctamente.', 'success')
    return redirect(url_for('cierre.index'))
