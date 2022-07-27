# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class PaymentType(models.Model):
    _name = 'payment.type'
    _description = 'Payment type'

    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for account in self:
            name = account.code + ' ' + account.name
            result.append((account.id, name))
        return result

    name = fields.Char(
            'Name', size=64, required=True, help='Payment type', translate=True
        )
    code = fields.Char(
            'Code', size=64, required=True,
            help='Specify the Code for Payment type'
        )
    suitable_bank_types = fields.Many2many(
            'res.partner.bank', 'bank_type_payment_type_rel',
            'pay_type_id', 'bank_type_id', 'Suitable bank types'
        )
    active = fields.Boolean('Active', default=True)
    note = fields.Text(
            'Description', translate=True,
            help='Description of the payment type that will be shown in the'
            ' invoices'
        )
    require_bank_account =fields.Boolean(
            'Require Bank Account',
            help='Ensure all lines in the payment order have a bank acount '
            'when proposing lines to be added in the payment order.'
        )
    company_id =fields.Many2one('res.company', 'Company', required=True)
    #lambda self, c: self.env['res.users'].browse(c).company_id.id


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    payment_type_id = fields.Many2one('payment.type', 'Payment type')
    
