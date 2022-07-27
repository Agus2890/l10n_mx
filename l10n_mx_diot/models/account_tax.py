# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models,fields

DIOT_TYPES = [
    ('vat_16', 'VAT 16%'),
    ('vat_11', 'VAT 11%'),
    ('vat_0', 'VAT 0%'),
    ('no_vat', 'No VAT'),
]


class AccountTax(models.Model):
    _inherit = "account.tax"

    diot_group = fields.Selection(DIOT_TYPES, 'DIOT group')