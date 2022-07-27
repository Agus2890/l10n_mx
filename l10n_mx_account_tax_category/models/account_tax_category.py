# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class AccountTaxCategory(models.Model):
    _name = 'account.tax.category'
    _description = "tax category sat"

    company_id = fields.Many2one('res.company', 'Company', required=True,
                    help='Campania', default =lambda self:
                    self.env['res.company']._company_default_get('account.tax.category'))
    name = fields.Char('Nombre', size=64, required=True,help='Nombre de la categoria')
    code = fields.Char('Code', size=32, required=True,help='Codigo')
    active = fields.Boolean('Active',help='Indicate if this category is active', default= 1)
    sign = fields.Integer('Sign')
    category_ids = fields.One2many('account.tax', 'tax_category_id',
                        'Category', help='Tax that belong of this category')
    code_sat=fields.Selection([('001','ISR'),('002','IVA'),('003','IEPS'),('ISH','ISH'),('Cedular','Cedular')], string='Impuesto')
    type=fields.Selection([('Tasa','Tasa'),('Cuota','Cuota'),('Exento','Exento'),('ISH','ISH'),('Cedular','Cedular')], string='Tipo Factor')


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_category_id = fields.Many2one('account.tax.category',
                'Categoria de Impuesto',help='Categoria del impuesto SAT')
