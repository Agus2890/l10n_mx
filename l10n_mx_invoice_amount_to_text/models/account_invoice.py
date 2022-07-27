# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from . import amount_to_text_es_MX


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('amount_total')
    def _get_amount_to_text(self):
        for invoice in self:
            amount_to_text = amount_to_text_es_MX.get_amount_to_text(
                self, invoice.amount_total, 'es_cheque', 'code' in invoice.\
                currency_id and invoice.currency_id.code or invoice.\
                currency_id.name)
            invoice.amount_to_text = amount_to_text       

    amount_to_text = fields.Char(compute='_get_amount_to_text',
            size=256, string='Amount to Text', store=True, copy=False,
            help='Amount of the invoice in letter')
