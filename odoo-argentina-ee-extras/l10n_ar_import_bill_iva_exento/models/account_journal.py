# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def create_document_from_attachment(self, attachment_ids=None):
        # OVERRIDE
        # Extensión para permitir IVA Exento: comentamos la restricción de código "1"
        journal = self or self.browse(self.env.context.get("default_journal_id"))

        # Para purchase: siempre permitir
        # Para sale: solo si l10n_ar_afip_pos es False
        # Línea original comentada:
        # and journal.company_id.l10n_ar_afip_responsibility_type_id.code == "1"
        if (
            (journal.type == "purchase" or (journal.type == "sale" and not journal.l10n_ar_is_pos))
            and journal.company_id.country_code == "AR"
            # and journal.company_id.l10n_ar_afip_responsibility_type_id.code == "1"
        ):
            attachments = self.env["ir.attachment"].browse(attachment_ids or [])

            if not attachments:
                raise UserError(_("No attachment was provided"))
            return journal.import_bills_from_xls(attachments)
        return super().create_document_from_attachment(attachment_ids)
