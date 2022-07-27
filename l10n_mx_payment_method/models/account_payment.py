# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


# class AccountAbstractPayment(models.AbstractModel):
#     _inherit = "account.abstract.payment"

#     payment_type_id = fields.Many2one(
#         'payment.type', string='Payment type'
#     )
#     require_bank_account = fields.Boolean(
#         string='Require Bank Account'
#     )
#     partner_bank_id = fields.Many2one(
#         'res.partner.bank', string='Partner Bank Account'
#     )    

#     @api.model
#     def default_get(self, fields):
#         rec = super(AccountAbstractPayment, self).default_get(fields)
#         invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
#         if invoice_defaults and len(invoice_defaults) == 1:
#             invoice = invoice_defaults[0]
#             rec['partner_bank_id'] = invoice['partner_bank_id'][0] if invoice['partner_bank_id'] else False
#             if invoice.get('type', False) == 'out_invoice' and invoice.get('paymethod', False) != 'PUE':
#                 rec['require_bank_account'] = True
#         return rec

#     @api.onchange('journal_id')
#     def _onchange_journal(self):
#         res = super(AccountAbstractPayment, self)._onchange_journal()
#         # if self.journal_id.type == 'bank':
#         #     self.require_bank_account = True
#         # else:
#         #     self.require_bank_account = False
#         if self.journal_id.payment_type_id:
#             self.payment_type_id = self.journal_id.payment_type_id.id if self.journal_id.payment_type_id else False
#         return res


# class AccountRegisterPayments(models.TransientModel):
#     _inherit = "account.register.payments"

#     @api.model
#     def default_get(self, fields):
#         rec = super(AccountRegisterPayments, self).default_get(fields)
#         active_ids = self._context.get('active_ids')

#         # Check bank for selected invoices ids
#         if active_ids:
#             invoice = self.env['account.invoice'].browse(active_ids[0])
#             rec['partner_bank_id'] = invoice.partner_bank_id.id if invoice.partner_bank_id else False
#         return rec

#     def _prepare_payment_vals(self, invoices):
#         res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)
#         if self.payment_type_id:
#             res.update({
#                 'payment_type_id': self.payment_type_id.id or False,
#                 'require_bank_account': self.require_bank_account or False,
#                 'partner_bank_id': self.partner_bank_id.id or False,
#                 })
#         return res


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_type_id = fields.Many2one(
        'payment.type', string='Payment type'
    )
    require_bank_account = fields.Boolean(
        string='Require Bank Account'
    )
    partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Partner Bank Account',
        states={'draft': [('readonly', False)]}
    )

    @api.onchange('partner_id')
    def _onchange_partner_bank_id(self):
        if self.partner_id:
            bank_ids = self.partner_id.bank_ids
            bank_id = bank_ids[0].id if bank_ids else False
            self.partner_bank_id = bank_id
