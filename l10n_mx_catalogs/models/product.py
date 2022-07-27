# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#     #_inherits = {'product.template': 'product_tmpl_id'}
#     @api.model
#     def create(self, vals):
#         product = super(ProductProduct, self).create(vals)
#         template_vals = {}
#         if 'code_product_sat' not in vals:
#             template_vals['code_product_sat'] = product.product_tmpl_id.code_product_sat.id
#         if 'product_unit_sat' not in vals:
#             template_vals['product_unit_sat'] = product.product_tmpl_id.product_unit_sat.id
#         if template_vals:
#             product.write(template_vals)
#         return product

#     code_product_sat=fields.Many2one('key.product.sat',string='Clave Producto Sat')
#     product_unit_sat=fields.Many2one('key.unit.sat',string='Clave Unidad Sat')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    code_product_sat=fields.Many2one('key.product.sat',string='Clave Producto Sat')
    product_unit_sat=fields.Many2one('key.unit.sat',string='Clave Unidad Sat')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # @api.onchange('categ_id')
    # def change_categ_id(self):
    #     if self.categ_id:
    #         self.code_product_sat = self.categ_id.code_product_sat.id
    #         self.product_unit_sat = self.categ_id.product_unit_sat.id
    #     else:
    #         self.code_product_sat = False
    #         self.product_unit_sat = False

    # def _update_sale_sat(self, vals):
    #     values={}
    #     if 'code_product_sat' in vals:
    #         values.update({'code_product_sat': vals['code_product_sat']})
    #     if 'product_unit_sat' in vals:
    #         values.update({'product_unit_sat':vals['product_unit_sat']})
    #     self.product_variant_ids.write(values)

    # @api.multi
    # def write(self, vals):
    #     res = super(ProductTemplate, self).write(vals)
    #     if 'code_product_sat' in vals:
    #         for product in self:
    #             product._update_sale_sat(vals)
    #     if 'product_unit_sat' in vals:
    #         for product in self:
    #             product._update_sale_sat(vals)
    #     return res

    # @api.model
    # def create(self, vals):
    #     product_tmpl = super(ProductTemplate, self).create(vals)
    #     if 'code_product_sat' in vals:
    #         for product in product_tmpl:
    #             product._update_sale_sat(vals)
    #     if 'product_unit_sat' in vals:
    #         for product in product_tmpl:
    #             product._update_sale_sat(vals)
    #     return product_tmpl
    
    code_product_sat=fields.Many2one('key.product.sat',string='Clave Producto Sat')
    product_unit_sat=fields.Many2one('key.unit.sat',string='Clave Unidad Sat')