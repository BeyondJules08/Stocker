import xml.etree.ElementTree as ET
from datetime import datetime

STORE_RFC = 'XEXX010101000'
STORE_NAME = 'Stocker SA de CV'
STORE_REGIMEN = '601'


def generar_cfdi_xml(folio_fiscal: str, venta, cliente, detalles, path: str):
    """Genera un XML con estructura CFDI 4.0 (simulación)."""
    fecha = (venta.fecha.strftime('%Y-%m-%dT%H:%M:%S')
             if venta.fecha else datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))

    forma_pago = '01' if venta.metodo_pago == 'Efectivo' else '04'

    ns = {
        'cfdi': 'http://www.sat.gob.mx/cfd/4',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }
    ET.register_namespace('cfdi', ns['cfdi'])
    ET.register_namespace('xsi', ns['xsi'])

    comprobante = ET.Element(f'{{{ns["cfdi"]}}}Comprobante', {
        f'{{{ns["xsi"]}}}schemaLocation': (
            'http://www.sat.gob.mx/cfd/4 '
            'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd'
        ),
        'Version': '4.0',
        'Serie': 'A',
        'Folio': folio_fiscal,
        'Fecha': fecha,
        'FormaPago': forma_pago,
        'SubTotal': f'{float(venta.subtotal):.2f}',
        'Moneda': 'MXN',
        'Total': f'{float(venta.total):.2f}',
        'TipoDeComprobante': 'I',
        'MetodoPago': 'PUE',
        'LugarExpedicion': '06600',
        'Exportacion': '01',
    })

    # Emisor
    ET.SubElement(comprobante, f'{{{ns["cfdi"]}}}Emisor', {
        'Rfc': STORE_RFC,
        'Nombre': STORE_NAME,
        'RegimenFiscal': STORE_REGIMEN,
    })

    # Receptor
    ET.SubElement(comprobante, f'{{{ns["cfdi"]}}}Receptor', {
        'Rfc': cliente.rfc,
        'Nombre': cliente.razon_social,
        'DomicilioFiscalReceptor': cliente.codigo_postal,
        'RegimenFiscalReceptor': _get_regimen_code(cliente.regimen_fiscal),
        'UsoCFDI': cliente.uso_cfdi,
    })

    # Conceptos
    conceptos = ET.SubElement(comprobante, f'{{{ns["cfdi"]}}}Conceptos')
    for d in detalles:
        nombre = d.producto.nombre if d.producto else 'Producto'
        precio_u = float(d.precio_unitario)
        subtotal = float(d.subtotal)
        iva_importe = round(subtotal * 0.16, 2)

        concepto = ET.SubElement(conceptos, f'{{{ns["cfdi"]}}}Concepto', {
            'ClaveProdServ': '43232408',
            'Cantidad': str(d.cantidad),
            'ClaveUnidad': 'H87',
            'Unidad': 'Pieza',
            'Descripcion': nombre,
            'ValorUnitario': f'{precio_u:.2f}',
            'Importe': f'{subtotal:.2f}',
            'ObjetoImp': '02',
        })

        impuestos_c = ET.SubElement(concepto, f'{{{ns["cfdi"]}}}Impuestos')
        traslados_c = ET.SubElement(impuestos_c, f'{{{ns["cfdi"]}}}Traslados')
        ET.SubElement(traslados_c, f'{{{ns["cfdi"]}}}Traslado', {
            'Base': f'{subtotal:.2f}',
            'Impuesto': '002',
            'TipoFactor': 'Tasa',
            'TasaOCuota': '0.160000',
            'Importe': f'{iva_importe:.2f}',
        })

    # Impuestos generales
    iva_total = float(venta.iva)
    impuestos = ET.SubElement(comprobante, f'{{{ns["cfdi"]}}}Impuestos', {
        'TotalImpuestosTrasladados': f'{iva_total:.2f}',
    })
    traslados = ET.SubElement(impuestos, f'{{{ns["cfdi"]}}}Traslados')
    ET.SubElement(traslados, f'{{{ns["cfdi"]}}}Traslado', {
        'Base': f'{float(venta.subtotal):.2f}',
        'Impuesto': '002',
        'TipoFactor': 'Tasa',
        'TasaOCuota': '0.160000',
        'Importe': f'{iva_total:.2f}',
    })

    tree = ET.ElementTree(comprobante)
    ET.indent(tree, space='  ')
    with open(path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)


def _get_regimen_code(regimen_fiscal: str) -> str:
    mapping = {
        'Sin obligaciones fiscales': '616',
        'General de Ley Personas Morales': '601',
        'Personas Físicas con Actividades Empresariales': '612',
        'Régimen de Incorporación Fiscal': '621',
    }
    return mapping.get(regimen_fiscal, '616')
