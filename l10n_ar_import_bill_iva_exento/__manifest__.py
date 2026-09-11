# -*- coding: utf-8 -*-
{
    'name': 'l10n_ar_import_bill IVA Exento',
    'version': '19.0.1.0',
    'category': 'Accounting/Localization',
    'summary': 'Extensión para permitir IVA Exento en importación de facturas',
    'description': '''
        Extiende el módulo l10n_ar_import_bill para permitir que empresas
        con IVA Exento puedan usar la funcionalidad de importación de facturas,
        removiendo la restricción que solo permite código AFIP "1".
        
        Comenta efectivamente la línea:
        and journal.company_id.l10n_ar_afip_responsibility_type_id.code == "1"
    ''',
    'author': 'ADHOC SA',
    'website': 'https://www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': ['l10n_ar_import_bill'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
