# -*- coding: utf-8 -*-
{
    'name': 'Bloquear pasar a borrador comprobantes validados en ARCA',
    'version': '19.0.1.0',
    'category': 'Accounting/Localization',
    'summary': 'Impide restablecer a borrador facturas y notas de credito con CAE de ARCA',
    'description': '''
        Bloquea "Restablecer a borrador" en facturas, notas de credito y notas
        de debito electronicas que ya fueron autorizadas por ARCA (tienen CAE).

        - Oculta el boton "Restablecer a borrador" en esos comprobantes.
        - Si igual se llama a button_draft, levanta un error.
        - Excepcion: el grupo "Restablecer a borrador comprobantes validados
          en ARCA" si puede, y queda registrado en el chatter.
        - Nadie puede cancelar ni eliminar un comprobante con CAE.

        Compatible con Odoo 18.0 en adelante.
    ''',
    'author': 'Aceleradora LA',
    'website': 'https://www.aceleradora.la',
    'license': 'AGPL-3',
    'depends': ['l10n_ar_edi'],
    'data': [
        'security/res_groups.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
