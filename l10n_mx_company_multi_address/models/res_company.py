# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    # def get_address_invoice_parent_company_id(self):
    #     res = {}
    #     partner_obj = self.env['res.partner']
    #     for company_id in self:
    #         partner_parent = company_id and company_id.parent_id and \
    #             company_id.parent_id.partner_id or False
    #         if partner_parent:
    #             address_id = partner_obj.address_get([partner_parent.id], ['invoice'])['invoice']
    #         # Validar, si tiene hijos utilizar no utilizar la main, mejor
    #         # utilizar la normal company_id.partner_id.id
    #         elif company_id.company_address_main_id:
    #             address_id = company_id.company_address_main_id.id
    #         else:
    #             address_id = partner_obj.address_get([company_id.partner_id.id], ['invoice'])['invoice']
    #         res[company_id.id] = address_id
    #     return res

    address_invoice_parent_company_id = fields.Many2one("res.partner",
            string='Dirección de Factura', help="In this field should \
            placed the address of the parent company , independently if \
            handled a scheme Multi-company o Multi-Address.",
            domain="[('type', '=', 'invoice')]")
