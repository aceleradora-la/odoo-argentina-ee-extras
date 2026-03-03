# -*- coding: utf-8 -*-
from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _is_ar_exempt_company(self):
        self.ensure_one()
        company = self.company_id
        return (
            company.country_code == "AR"
            and company.l10n_ar_afip_responsibility_type_id
            and company.l10n_ar_afip_responsibility_type_id.code == "4"
        )

    def _is_foreign_partner(self):
        self.ensure_one()
        partner_country = self.partner_id.country_id
        return bool(partner_country and partner_country.code and partner_country.code != "AR")

    @api.depends(
        "company_id",
        "company_id.l10n_ar_afip_responsibility_type_id",
        "partner_id",
        "partner_id.country_id",
    )
    def _compute_l10n_latam_available_document_types(self):
        super()._compute_l10n_latam_available_document_types()
        export_doc_type = self.env["l10n_latam.document.type"].search(
            [("country_id.code", "=", "AR"), ("code", "=", "19")], limit=1
        )
        if not export_doc_type:
            return

        for move in self:
            if (
                move.move_type in ("out_invoice", "out_refund")
                and move._is_ar_exempt_company()
                and move._is_foreign_partner()
            ):
                move.l10n_latam_available_document_type_ids |= export_doc_type

    @api.model
    def wsfex_get_cae_request(self, last_id, client):
        res = super().wsfex_get_cae_request(last_id, client)
        if not self:
            return res

        self.ensure_one()
        is_export_19 = self.l10n_latam_document_type_id.code == "19"
        if is_export_19 and self._is_ar_exempt_company() and int(self.l10n_ar_afip_concept) == 1:
            array_of_permissions = client.get_type("ns0:ArrayOfPermiso")
            permisos = self._get_permissions()
            res.update({"Permisos": array_of_permissions(permisos) if permisos else None})
            res.update({"Permiso_existente": "S" if permisos else "N"})
        return res
