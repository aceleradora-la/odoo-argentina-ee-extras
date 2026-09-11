# -*- coding: utf-8 -*-
{
    'name': 'SICORE Percepciones IVA (RG 5329)',
    'version': '19.0.1.0',
    'category': 'Accounting/Localization',
    'summary': 'Reporte y exportable SICORE de percepciones de IVA (impuesto 767, regimen 602)',
    'description': '''
        Agrega el reporte contable "SICORE Percepciones IVA (AR)" con los mismos
        botones de exportacion que el SICORE de retenciones de ganancias.

        Genera los dos archivos de ancho fijo que pide SICORE:
          - sicoreim.txt : percepciones practicadas (198 caracteres por renglon)
          - sicoresu.txt : datos de los sujetos percibidos (83 caracteres)

        Toma las lineas de impuesto de facturas, notas de debito y notas de credito
        de venta cuyo impuesto tenga cargado el Codigo de ARCA 602.
    ''',
    'author': 'Aceleradora LA',
    'website': 'https://www.aceleradora.la',
    'license': 'AGPL-3',
    'depends': [
        'account_reports',
        'l10n_ar_withholding',
    ],
    'data': [
        'data/account_report_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
