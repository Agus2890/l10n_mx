# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResCountryStateCity(models.Model):
    _description = "Country state city"
    _name = 'res.country.state.city'
    _order = 'name'

    name = fields.Char('Name', size=64, required=True, index=True,help='Administrative divisions of a state.')
    state_id = fields.Many2one('res.country.state', 'State', required=True)
    country_id = fields.Many2one('res.country', related='state_id.country_id', string='Country', store=True, readonly=True)
    code = fields.Char('City Code', size=5, help='The city code in max. five chars.')