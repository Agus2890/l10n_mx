# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_line_id = fields.Many2one('account.invoice.line', string='Invoice line id')

    @api.multi
    def assert_balanced(self):
        res = super(AccountMoveLine, self).assert_balanced()
        if not self.ids:
            return True
        prec = self.env['decimal.precision'].precision_get('Account')

        self._cr.execute("""\
            SELECT      move_id
            FROM        account_move_line
            WHERE       move_id in %s
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) > %s
            """, (tuple(self.ids), 10 ** (-max(5, prec))))
        if self.invoice_id.amount_discount == 0.0:
            if len(self._cr.fetchall()) != 0:
                raise UserError(_("Cannot create unbalanced journal entry."))
        return res#True

