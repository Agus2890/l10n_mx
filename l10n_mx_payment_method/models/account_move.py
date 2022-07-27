# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # @api.one
    # @api.depends('move_id.line_ids.amount_residual')
    # def _compute_payments(self):
    #     payment_lines = []
    #     res = super(AccountMove, self)._compute_payments()
    #     for line in self.move_id.line_ids:
    #         payment_lines.extend(filter(None, [rp.credit_move_id.id for rp in line.matched_credit_ids]))
    #         payment_lines.extend(filter(None, [rp.debit_move_id.id for rp in line.matched_debit_ids]))
    #     self.payment_move_ids = self.env['account.move.line'].browse(list(set(payment_lines)))
    #     return res

    payment_type_id = fields.Many2one('payment.type', 'Forma de Pago',
       help='Indicates the way it was paid or will be paid the invoice,'
            'where the options could be: check, bank transfer, reservoir in '
            'account bank, credit card, cash etc. If not know as will be '
            'paid the invoice, leave empty and the XML show “Unidentified”.')
    # payment_move_ids = fields.Many2many('account.move.line','rel_move', string='Payments',
    #     compute='_compute_payments', store=True)

    # @api.onchange('partner_id', 'company_id')
    # def _onchange_partner_id(self):
    #     result = super(AccountInvoice, self)._onchange_partner_id()
    #     if self.partner_id:
    #         if self.type in ('in_invoice', 'in_refund'):
    #             self.payment_type_id = self.partner_id.payment_type_supplier_id.id
    #         else:
    #             self.payment_type_id = self.partner_id.payment_type_customer_id.id
    #     if self.type in ('in_invoice', 'out_invoice'):
    #         bank_ids = self.partner_id.bank_ids
    #         bank_id = bank_ids[0].id if bank_ids else False
    #         self.partner_bank_id = bank_id
    #     return result