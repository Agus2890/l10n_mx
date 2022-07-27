# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    address_invoice_company_id = fields.Many2one('res.partner',
            string='Invoice Company Address', domain="[('type', '=', 'invoice')]",
            help='If this field is fill, the electronic invoice will take \
            this address as issuing address')
    company2_id = fields.Many2one("res.company", string='Company Emitter',
            help="If this field is fill, the electronic invoice will take the \
            data of this company as emitter company.")
