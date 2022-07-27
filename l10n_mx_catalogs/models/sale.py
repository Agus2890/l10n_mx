# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # def _prepare_invoice(self):
    #     res = super(SaleOrder, self)._prepare_invoice()
    #     method = ''
    #     if self.payment_term_id:

    #         payment = self.payment_term_id.line_ids
    #         if payment.days <= 0:
    #             method = 'PUE'
    #         elif payment.days > 0:
    #             method = 'PPD'
    #         if not payment:
    #             raise UserError(_("Plazo de pago no cuenta rango de dias ('rango minimo es 0')"))    
    #     if not self.payment_term_id:
    #         raise UserError(_("Plazo de pago sin asignar"))
    #     return res

# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     code_product_sat = fields.Many2one('key.product.sat',string='Clave Producto Sat')
#     product_unit_sat = fields.Many2one('key.unit.sat',string='Clave Unidad Sat') 



# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"

#     code_product_sat = fields.Many2one('key.product.sat',string='Clave Producto Sat')
#     product_unit_sat = fields.Many2one('key.unit.sat',string='Clave Unidad Sat')   