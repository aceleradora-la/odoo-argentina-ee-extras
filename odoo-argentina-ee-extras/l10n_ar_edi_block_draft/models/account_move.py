from odoo import api, models
from odoo.exceptions import UserError

from odoo.addons.l10n_ar_edi.models.account_move import AccountMove as L10nArEdiAccountMove


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_ar_filter_validated_in_arca(self):
        """Comprobantes de un punto de venta electronico autorizados por ARCA (con CAE)."""
        return self.filtered(lambda move: move.journal_id.l10n_ar_afip_ws and move.l10n_ar_afip_auth_code)

    @api.model
    def _l10n_ar_user_can_reset_arca_validated(self):
        return self.env.user.has_group('l10n_ar_edi_block_draft.group_arca_reset_draft')

    @api.depends('l10n_ar_afip_auth_code', 'journal_id.l10n_ar_afip_ws')
    @api.depends_context('uid')
    def _compute_show_reset_to_draft_button(self):
        # EXTENDS 'account'
        super()._compute_show_reset_to_draft_button()
        validated = self._l10n_ar_filter_validated_in_arca()
        if not validated:
            return
        if self._l10n_ar_user_can_reset_arca_validated():
            # l10n_ar_edi oculta el boton en los comprobantes con CAE (l10n_ar_edi_ux de ADHOC lo
            # anula con un monkey patch). Para el grupo autorizado se recalcula con las reglas que
            # quedan por debajo de l10n_ar_edi (las de account: hash, estado, cancelacion pendiente),
            # asi el boton aparece haya o no haya patch.
            super(L10nArEdiAccountMove, validated)._compute_show_reset_to_draft_button()
        else:
            validated.show_reset_to_draft_button = False

    def _check_draftable(self):
        # EXTENDS 'account': button_draft pasa por aca antes de pasar a borrador.
        validated = self._l10n_ar_filter_validated_in_arca()
        if validated and not self._l10n_ar_user_can_reset_arca_validated():
            raise UserError(self.env._(
                "No se puede restablecer a borrador un comprobante ya validado en ARCA (con CAE). "
                "Para anularlo, emití la nota de crédito o débito correspondiente.\n\n%s",
                "\n".join(validated.mapped('name')),
            ))
        return super()._check_draftable()

    def button_draft(self):
        # EXTENDS 'account': deja constancia en el chatter cuando el grupo autorizado lo usa.
        validated = self._l10n_ar_filter_validated_in_arca()
        res = super().button_draft()
        for move in validated:
            move.message_post(body=self.env._(
                "Comprobante validado en ARCA (CAE %s) restablecido a borrador. Lo que se cambie no "
                "se informa a ARCA: no modificar cliente, fecha, importes ni impuestos.",
                move.l10n_ar_afip_auth_code,
            ))
        return res

    def button_cancel(self):
        # EXTENDS 'account': ni siquiera el grupo autorizado puede cancelar un comprobante con CAE.
        validated = self._l10n_ar_filter_validated_in_arca()
        if validated:
            raise UserError(self.env._(
                "No se puede cancelar un comprobante ya validado en ARCA (con CAE). "
                "Para anularlo, emití la nota de crédito o débito correspondiente.\n\n%s",
                "\n".join(validated.mapped('name')),
            ))
        return super().button_cancel()

    @api.ondelete(at_uninstall=False)
    def _unlink_except_validated_in_arca(self):
        # Un comprobante con CAE pasado a borrador por el grupo autorizado no se puede borrar.
        validated = self._l10n_ar_filter_validated_in_arca()
        if validated:
            raise UserError(self.env._(
                "No se puede eliminar un comprobante ya validado en ARCA (con CAE).\n\n%s",
                "\n".join(validated.mapped('name')),
            ))
