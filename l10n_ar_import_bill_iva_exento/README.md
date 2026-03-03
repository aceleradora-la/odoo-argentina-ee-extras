# l10n_ar_import_bill IVA Exento

Módulo de extensión para `l10n_ar_import_bill` que permite que empresas con IVA Exento puedan usar la funcionalidad de importación de facturas.

## Descripción

Este módulo comenta efectivamente la restricción que solo permitía empresas con código AFIP "1" (Responsable Inscripto) usar la importación de facturas desde Excel.

La línea original que se comenta es:
```python
and journal.company_id.l10n_ar_afip_responsibility_type_id.code == "1"
```

## Instalación

1. Colocar este módulo en la ruta de addons de Odoo
2. Actualizar la lista de aplicaciones
3. Instalar el módulo `l10n_ar_import_bill_iva_exento`

## Dependencias

- `l10n_ar_import_bill`

## Compatibilidad

Este módulo está diseñado para funcionar en todas las ramas donde exista el módulo base `l10n_ar_import_bill`.

## Autor

ADHOC SA - https://www.adhoc.com.ar
