import os
import uuid
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, send_file, abort, current_app)
from flask_login import login_required, current_user
from app import db
from app.models import Factura, Venta, Cliente
from app.utils.pdf_generator import generar_factura_pdf
from app.utils.xml_generator import generar_cfdi_xml

facturas_bp = Blueprint('facturas', __name__)


def _require_operativo():
    if current_user.rol.nombre != 'operativo':
        abort(403)


@facturas_bp.route('/')
@login_required
def index():
    _require_operativo()
    facturas = (Factura.query
                .order_by(Factura.fecha_emision.desc())
                .all())
    return render_template('facturas/index.html', facturas=facturas)


@facturas_bp.route('/pendientes')
@login_required
def pendientes():
    _require_operativo()
    ventas = (Venta.query
              .filter_by(facturada=False)
              .filter(Venta.cliente_id.isnot(None))
              .filter(Venta.estado == 'completada')
              .order_by(Venta.fecha.desc())
              .all())
    return render_template('facturas/pendientes.html', ventas=ventas)


@facturas_bp.route('/generar/<int:venta_id>', methods=['POST'])
@login_required
def generar(venta_id):
    _require_operativo()
    venta = Venta.query.get_or_404(venta_id)

    if venta.facturada:
        flash('Esta venta ya fue facturada.', 'warning')
        return redirect(url_for('facturas.index'))

    if not venta.cliente_id:
        flash('La venta no tiene cliente asignado para facturar.', 'danger')
        return redirect(url_for('facturas.pendientes'))

    cliente = Cliente.query.get(venta.cliente_id)
    folio_fiscal = str(uuid.uuid4()).upper()
    detalles = venta.detalles

    doc_dir = current_app.config['PDF_FOLDER']
    pdf_filename = f'factura_{folio_fiscal}.pdf'
    xml_filename = f'factura_{folio_fiscal}.xml'
    pdf_path = os.path.join(doc_dir, pdf_filename)
    xml_path = os.path.join(doc_dir, xml_filename)

    generar_factura_pdf(folio_fiscal, venta, cliente, detalles, pdf_path)
    generar_cfdi_xml(folio_fiscal, venta, cliente, detalles, xml_path)

    factura = Factura(
        folio_fiscal=folio_fiscal,
        venta_id=venta.id,
        cliente_id=cliente.id,
        xml_url=f'/facturas/documentos/{xml_filename}',
        pdf_url=f'/facturas/documentos/{pdf_filename}',
        subtotal=venta.subtotal,
        iva=venta.iva,
        total=venta.total,
    )
    venta.facturada = True
    db.session.add(factura)
    db.session.commit()

    flash(f'Factura {folio_fiscal[:8]}... generada correctamente.', 'success')
    return redirect(url_for('facturas.detalle', factura_id=factura.id))


@facturas_bp.route('/<int:factura_id>')
@login_required
def detalle(factura_id):
    _require_operativo()
    factura = Factura.query.get_or_404(factura_id)
    return render_template('facturas/detalle.html', factura=factura)


@facturas_bp.route('/<int:factura_id>/pdf')
@login_required
def descargar_pdf(factura_id):
    _require_operativo()
    factura = Factura.query.get_or_404(factura_id)
    filename = os.path.basename(factura.pdf_url)
    path = os.path.join(current_app.config['PDF_FOLDER'], filename)
    return send_file(path, as_attachment=True, mimetype='application/pdf')


@facturas_bp.route('/<int:factura_id>/xml')
@login_required
def descargar_xml(factura_id):
    _require_operativo()
    factura = Factura.query.get_or_404(factura_id)
    filename = os.path.basename(factura.xml_url)
    path = os.path.join(current_app.config['PDF_FOLDER'], filename)
    return send_file(path, as_attachment=True, mimetype='application/xml')
