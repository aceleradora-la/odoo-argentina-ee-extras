# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError

COD_IMPUESTO = '0767'      # IVA
COD_REGIMEN = '602'        # RG 5329/2023. Tambien el Codigo de ARCA del impuesto en Odoo.
COD_OPERACION = '2'        # 2 = percepcion
COD_CONDICION = '13'       # 13 = venta de cosas muebles y locacion, alicuota general
                           # 14 = alicuota reducida (percepcion 1,5% sobre ventas al 10,5%)

# Base de calculo en las notas de credito:
#   'percepcion' -> replica el sistema anterior (base = importe percibido)
#   'neto'       -> criterio del instructivo (base = neto gravado)
BASE_NOTA_CREDITO = 'percepcion'

# Exportar solo comprobantes autorizados por ARCA. El campo se detecta solo.
SOLO_AUTORIZADOS = True
CAMPOS_CAE = ['l10n_ar_afip_auth_code', 'afip_auth_code']

# Si hay comprobantes que no se pueden exportar, cortar en vez de omitirlos.
ESTRICTO = True

# Codigo de comprobante SICORE segun el codigo ARCA del tipo de documento.
# 01 Factura | 02 Recibo | 03 Nota de Credito | 04 Nota de Debito | 06 Orden de Pago
SICORE_COMPROBANTE = {
    '1': '01', '6': '01', '11': '01', '19': '01', '20': '01', '21': '01', '51': '01',
    '81': '01', '82': '01', '83': '01', '111': '01', '118': '01',
    '201': '01', '206': '01', '211': '01',
    '2': '04', '7': '04', '12': '04', '52': '04', '202': '04', '207': '04', '212': '04',
    '3': '03', '8': '03', '13': '03', '53': '03', '203': '03', '208': '03', '213': '03',
    '110': '03', '112': '03', '113': '03', '114': '03', '115': '03', '119': '03', '120': '03',
}


# --------------------------------------------------------------------------
# Formateo de campos de ancho fijo
# --------------------------------------------------------------------------

def der(valor, ancho):
    """Importe alineado a derecha con espacios, decimales con coma."""
    return ('%.2f' % abs(valor)).replace('.', ',').rjust(ancho)


def ceros(valor, ancho):
    """Importe alineado a derecha rellenado con ceros."""
    return ('%.2f' % abs(valor)).replace('.', ',').zfill(ancho)


def txt(valor, ancho):
    """Texto truncado y alineado a izquierda."""
    return (valor or '')[:ancho].ljust(ancho)


def digitos(valor):
    return ''.join([c for c in (valor or '') if c.isdigit()])


def linea_percepcion(cod_comprobante, fecha, nro_comprobante, importe_comprobante,
                     base_calculo, importe_percibido, cuit):
    """Renglon de 198 caracteres del archivo de retenciones y percepciones."""
    linea = (
        cod_comprobante.zfill(2)            #  1 codigo de comprobante        2
        + fecha.strftime('%d/%m/%Y')        #  2 fecha del comprobante       10
        + nro_comprobante.zfill(16)         #  3 numero de comprobante       16
        + der(importe_comprobante, 16)      #  4 importe del comprobante     16
        + COD_IMPUESTO.zfill(4)             #  5 codigo de impuesto           4
        + COD_REGIMEN.zfill(3)              #  6 codigo de regimen            3
        + COD_OPERACION                     #  7 codigo de operacion          1
        + der(base_calculo, 14)             #  8 base de calculo             14
        + fecha.strftime('%d/%m/%Y')        #  9 fecha de la percepcion      10
        + COD_CONDICION.rjust(2)            # 10 codigo de condicion          2
        + '0'                               # 11 sujeto suspendido            1
        + ceros(importe_percibido, 14)      # 12 importe percibido           14
        + der(0, 6)                         # 13 porcentaje de exclusion      6
        + ' ' * 10                          # 14 fecha boletin               10
        + '80'                              # 15 tipo de documento            2
        + txt(cuit, 20)                     # 16 numero de documento         20
        + '0' * 14                          # 17 nro certificado original    14
        + ' ' * 30                          # 18 denominacion del ordenante  30
        + '0'                               # 19 acrecentamiento              1
        + '0' * 11                          # 20 cuit pais del retenido      11
        + '0' * 11                          # 21 cuit del ordenante          11
    )
    if len(linea) != 198:
        raise UserError(_('Renglon de %(n)s caracteres en vez de 198: %(l)s',
                          n=len(linea), l=linea))
    return linea


def linea_sujeto(cuit, denominacion, domicilio, localidad, cp):
    """Renglon de 83 caracteres del archivo de sujetos."""
    linea = (
        cuit.zfill(11)                      # cuit                           11
        + txt(denominacion, 20)             # denominacion                   20
        + txt(domicilio, 20)                # domicilio                      20
        + txt(localidad, 20)                # localidad                      20
        + txt(digitos(cp).zfill(6), 10)     # codigo postal                  10
        + '80'                              # tipo de documento               2
    )
    if len(linea) != 83:
        raise UserError(_('Renglon de %(n)s caracteres en vez de 83: %(l)s',
                          n=len(linea), l=linea))
    return linea


# --------------------------------------------------------------------------
# Custom handler del reporte
# --------------------------------------------------------------------------

class L10nArSicorePercepcionesHandler(models.AbstractModel):
    _name = 'l10n_ar.sicore.percepciones.handler'
    _inherit = 'account.report.custom.handler'
    _description = 'SICORE - Percepciones de IVA RG 5329/2023'

    def _custom_options_initializer(self, report, options, previous_options):
        super()._custom_options_initializer(report, options, previous_options)
        options.setdefault('buttons', []).extend([
            {
                'name': _('TXT SICORE Percepciones'),
                'sequence': 80,
                'action': 'export_file',
                'action_param': 'l10n_ar_export_percepciones_txt',
                'file_export_type': _('TXT'),
            },
            {
                'name': _('TXT SICORE Sujetos'),
                'sequence': 81,
                'action': 'export_file',
                'action_param': 'l10n_ar_export_sujetos_txt',
                'file_export_type': _('TXT'),
            },
        ])

    # -- botones -----------------------------------------------------------

    def l10n_ar_export_percepciones_txt(self, options):
        percepciones, dummy = self._l10n_ar_sicore_lineas(options)
        return self._l10n_ar_sicore_archivo('sicoreim.txt', percepciones)

    def l10n_ar_export_sujetos_txt(self, options):
        dummy, sujetos = self._l10n_ar_sicore_lineas(options)
        return self._l10n_ar_sicore_archivo('sicoresu.txt', sujetos)

    def _l10n_ar_sicore_archivo(self, nombre, renglones):
        contenido = '\r\n'.join(renglones) + '\r\n'
        return {
            'file_name': nombre,
            'file_content': contenido.encode('latin-1', 'replace'),
            'file_type': 'txt',
        }

    # -- extraccion --------------------------------------------------------

    def _l10n_ar_sicore_impuestos(self):
        impuestos = self.env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('l10n_ar_code', '=', COD_REGIMEN),
        ])
        if not impuestos:
            raise UserError(_(
                'No hay impuestos de venta con Codigo de ARCA = %s. Cargalo en el '
                'impuesto de percepcion de IVA para que el reporte lo reconozca.',
                COD_REGIMEN))
        return impuestos

    def _l10n_ar_sicore_dominio(self, options):
        dominio = [
            ('tax_line_id', 'in', self._l10n_ar_sicore_impuestos().ids),
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
            ('move_id.invoice_date', '>=', options['date']['date_from']),
            ('move_id.invoice_date', '<=', options['date']['date_to']),
        ]
        if not options.get('all_entries'):
            dominio.append(('parent_state', '=', 'posted'))

        companias = [c['id'] for c in options.get('companies') or []]
        if companias:
            dominio.append(('company_id', 'in', companias))

        if SOLO_AUTORIZADOS:
            campos = self.env['account.move']._fields
            cae = [c for c in CAMPOS_CAE if c in campos]
            if cae:
                dominio.append(('move_id.' + cae[0], '!=', False))
        return dominio

    def _l10n_ar_sicore_lineas(self, options):
        """Devuelve (renglones de sicoreim, renglones de sicoresu)."""
        lineas_impuesto = self.env['account.move.line'].search(
            self._l10n_ar_sicore_dominio(options))
        if not lineas_impuesto:
            raise UserError(_('No hay percepciones en el periodo seleccionado.'))

        # Un comprobante puede tener mas de una linea del mismo impuesto.
        acumulado = {}
        for aml in lineas_impuesto:
            datos = acumulado.setdefault(aml.move_id, {'perc': 0.0, 'base': 0.0})
            datos['perc'] += abs(aml.balance)
            datos['base'] += abs(aml.tax_base_amount)

        problemas = []
        validos = []
        for move in acumulado:
            partner = move.commercial_partner_id
            if len(digitos(partner.vat)) != 11:
                problemas.append(_('%(mv)s: %(pt)s no tiene un CUIT valido (%(vat)s)',
                                   mv=move.name, pt=partner.display_name,
                                   vat=partner.vat or '-'))
            elif not move.invoice_date:
                problemas.append(_('%s: sin fecha de factura', move.name))
            elif (move.l10n_latam_document_type_id.code or '') not in SICORE_COMPROBANTE:
                problemas.append(
                    _('%(mv)s: tipo de comprobante ARCA %(cd)s sin equivalente en SICORE',
                      mv=move.name, cd=move.l10n_latam_document_type_id.code or '-'))
            else:
                validos.append(move)

        if problemas and ESTRICTO:
            raise UserError(_('No puedo exportar estos comprobantes:\n\n%s',
                              '\n'.join(problemas)))

        percepciones = []
        sujetos = {}
        for move in sorted(validos, key=lambda m: (m.invoice_date, m.name)):
            datos = acumulado[move]
            partner = move.commercial_partner_id
            cuit = digitos(partner.vat)

            base = datos['base']
            if move.move_type == 'out_refund' and BASE_NOTA_CREDITO == 'percepcion':
                base = datos['perc']

            percepciones.append(linea_percepcion(
                SICORE_COMPROBANTE[move.l10n_latam_document_type_id.code],
                move.invoice_date,
                digitos(move.l10n_latam_document_number or move.name),
                move.amount_total_signed,
                base,
                datos['perc'],
                cuit,
            ))

            if cuit not in sujetos:
                sujetos[cuit] = linea_sujeto(
                    cuit, partner.name, partner.street, partner.city, partner.zip)

        return percepciones, list(sujetos.values())
