# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('vat')
    def _get_base_vat_split(self):
        for rfc in self:
           rfc.vat_split = rfc.vat and rfc.vat[2:] or False
        #res = {}
        #for partner in self:
        #    res[partner.id] = partner.vat and partner.vat[2:] or False
        #return res

    vat_split = fields.Char(compute='_get_base_vat_split', string='VAT Split', store=True,
                                help='Remove the prefix of the country of the VAT')
