# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_discount_income_categ_id = fields.Many2one('account.account', string='Sale Discount Account')
    property_account_discount_expense_categ_id = fields.Many2one('account.account', string='Purche Discount Account')
