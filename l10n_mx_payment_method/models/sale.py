# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('pricelist_id', 'order_line')
    def _onchange_pricelist_id(self):
        res=super(SaleOrder,self)._onchange_pricelist_id()
        rate=self.currency_id.with_context(date=self.date_order).rate or 1.0
        self.rate=1/self.currency_rate
        return res

    # @api.depends('pricelist_id', 'date_order', 'company_id')
    # def _compute_currency_rate(self):
    #     res=super(SaleOrder,self)._compute_currency_rate()
    #     rate=self.currency_id.with_context(date=self.date_order).rate or 1.0
    #     self.rate=1/self.currency_rate
    #     return res

    payment_type_id= fields.Many2one('payment.type', string='Forma de Pago')
    rate = fields.Float(string = 'T.C', copy=False,digits=(12, 2))
