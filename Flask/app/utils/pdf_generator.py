from datetime import datetime
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                Paragraph, Spacer, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

STORE_NAME = 'Stocker SA de CV'
STORE_RFC = 'XEXX010101000'
STORE_ADDR = 'Av. Comercio 100, CDMX, México'
STORE_PHONE = '55 0000 0000'


def generar_ticket_pdf(venta, detalles, path: str):
    """Ticket de venta estilo caja registradora (papel angosto)."""
    doc = SimpleDocTemplate(
        path,
        pagesize=(80 * mm, 297 * mm),
        leftMargin=4 * mm, rightMargin=4 * mm,
        topMargin=5 * mm, bottomMargin=5 * mm,
    )
    styles = getSampleStyleSheet()
    center = ParagraphStyle('center', parent=styles['Normal'],
                            alignment=TA_CENTER, fontSize=8)
    bold_center = ParagraphStyle('bold_center', parent=styles['Normal'],
                                 alignment=TA_CENTER, fontSize=9,
                                 fontName='Helvetica-Bold')
    small = ParagraphStyle('small', parent=styles['Normal'], fontSize=7)

    story = []

    story.append(Paragraph(STORE_NAME, bold_center))
    story.append(Paragraph(f'RFC: {STORE_RFC}', center))
    story.append(Paragraph(STORE_ADDR, center))
    story.append(Paragraph(f'Tel: {STORE_PHONE}', center))
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width='100%', thickness=0.5))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph(f'Folio: {venta.folio}', small))
    fecha_str = venta.fecha.strftime('%d/%m/%Y %H:%M') if venta.fecha else ''
    story.append(Paragraph(f'Fecha: {fecha_str}', small))
    story.append(Paragraph(f'Pago: {venta.metodo_pago}', small))
    story.append(Spacer(1, 3 * mm))

    # Products table
    col_w = [30 * mm, 10 * mm, 15 * mm, 16 * mm]
    table_data = [['Producto', 'Cant', 'P.Unit', 'Importe']]
    for d in detalles:
        table_data.append([
            d.producto.nombre[:22] if d.producto else '—',
            str(d.cantidad),
            f'${float(d.precio_unitario):,.2f}',
            f'${float(d.subtotal):,.2f}',
        ])

    t = Table(table_data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t)
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width='100%', thickness=0.5))

    right = ParagraphStyle('right', parent=styles['Normal'],
                           alignment=TA_RIGHT, fontSize=8)
    bold_right = ParagraphStyle('bold_right', parent=styles['Normal'],
                                alignment=TA_RIGHT, fontSize=9,
                                fontName='Helvetica-Bold')

    story.append(Paragraph(f'Subtotal: ${float(venta.subtotal):,.2f}', right))
    story.append(Paragraph(f'IVA (16%): ${float(venta.iva):,.2f}', right))
    story.append(Paragraph(f'TOTAL: ${float(venta.total):,.2f}', bold_right))

    if venta.monto_recibido:
        story.append(Paragraph(
            f'Recibido: ${float(venta.monto_recibido):,.2f}', right))
        story.append(Paragraph(
            f'Cambio: ${float(venta.cambio or 0):,.2f}', right))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('¡Gracias por su compra!', center))

    doc.build(story)


def generar_factura_pdf(folio_fiscal: str, venta, cliente, detalles, path: str):
    """Factura formal en hoja A4."""
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Heading1'],
                                 fontSize=16, alignment=TA_CENTER)
    subtitle = ParagraphStyle('subtitle', parent=styles['Normal'],
                              fontSize=10, alignment=TA_CENTER)
    label = ParagraphStyle('label', parent=styles['Normal'],
                           fontSize=8, textColor=colors.grey)
    value = ParagraphStyle('value', parent=styles['Normal'], fontSize=9)
    right = ParagraphStyle('right', parent=styles['Normal'],
                           alignment=TA_RIGHT, fontSize=9)
    bold_right = ParagraphStyle('bold_right', parent=styles['Normal'],
                                alignment=TA_RIGHT, fontSize=10,
                                fontName='Helvetica-Bold')

    story = []

    # Header
    story.append(Paragraph('COMPROBANTE FISCAL DIGITAL', title_style))
    story.append(Paragraph('(Simulación CFDI 4.0)', subtitle))
    story.append(Spacer(1, 0.3 * cm))

    # Folio UUID
    story.append(Paragraph(f'Folio Fiscal: {folio_fiscal}', label))
    fecha_str = venta.fecha.strftime('%Y-%m-%dT%H:%M:%S') if venta.fecha else ''
    story.append(Paragraph(f'Fecha de Emisión: {fecha_str}', label))
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width='100%'))
    story.append(Spacer(1, 0.3 * cm))

    # Emisor / Receptor
    emisor_receptor = [
        ['EMISOR', 'RECEPTOR'],
        [Paragraph(f'<b>{STORE_NAME}</b><br/>RFC: {STORE_RFC}<br/>'
                   f'Régimen: 601 - General de Ley PM<br/>'
                   f'Dirección: {STORE_ADDR}', value),
         Paragraph(f'<b>{cliente.razon_social}</b><br/>RFC: {cliente.rfc}<br/>'
                   f'Régimen: {cliente.regimen_fiscal}<br/>'
                   f'Uso CFDI: {cliente.uso_cfdi}<br/>'
                   f'Dirección: {cliente.direccion_fiscal}<br/>'
                   f'C.P.: {cliente.codigo_postal}', value)],
    ]
    t = Table(emisor_receptor, colWidths=[9 * cm, 9 * cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    # Products
    col_w = [5.5 * cm, 1.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm]
    table_data = [['Descripción', 'Cant', 'P.Unitario', 'Descuento', 'Imp.', 'Importe']]
    for d in detalles:
        nombre = d.producto.nombre if d.producto else '—'
        table_data.append([
            nombre,
            str(d.cantidad),
            f'${float(d.precio_unitario):,.2f}',
            '$0.00',
            f'${float(d.subtotal * Decimal("0.16")):,.2f}',
            f'${float(d.subtotal):,.2f}',
        ])

    from decimal import Decimal
    t2 = Table(table_data, colWidths=col_w, repeatRows=1)
    t2.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e94560')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.5 * cm))

    # Totals
    totals_data = [
        ['', 'Subtotal:', f'${float(venta.subtotal):,.2f}'],
        ['', 'IVA (16%):', f'${float(venta.iva):,.2f}'],
        ['', 'TOTAL:', f'${float(venta.total):,.2f}'],
    ]
    t3 = Table(totals_data, colWidths=[11 * cm, 4 * cm, 3 * cm])
    t3.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (1, 2), (-1, 2), 'Helvetica-Bold'),
        ('LINEABOVE', (1, 2), (-1, 2), 1, colors.black),
        ('FONTSIZE', (1, 2), (-1, 2), 11),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width='100%'))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        'Este documento es una simulación de CFDI. No tiene validez fiscal.',
        ParagraphStyle('footer', parent=styles['Normal'],
                       fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
