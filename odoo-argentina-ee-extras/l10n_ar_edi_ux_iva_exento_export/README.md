# l10n_ar_edi_ux IVA Exento Export

Small extension for `l10n_ar_edi_ux` to allow exempt companies (AFIP code `4`) to issue export
invoices with document type `19` for foreign partners.

## What it changes

- Extends `account.move` and adds document type `19` to
  `l10n_latam_available_document_type_ids` when:
  - company is AR and IVA Exento (`l10n_ar_afip_responsibility_type_id.code == "4"`),
  - partner is foreign (`country_id.code != "AR"`),
  - move is customer invoice or credit note.
- Keeps `wsfex_get_cae_request` compatible for exempt companies using export document `19`.

## Dependency

- `l10n_ar_edi_ux`
