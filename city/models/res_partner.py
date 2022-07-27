# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one('res.country.state.city', 'City')

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if (not view_id) and (view_type == 'form') and self._context.get('force_email'):
            view_id = self.env.ref('base.view_partner_simple_form').id
        res = super(ResPartner, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            res['arch'] = self._fields_view_get_address(res['arch'])
        return res
    
    @api.onchange('city_id')
    def onchange_city(self):
        if self.city_id:
            city = self.env['res.country.state.city'].browse(self.city_id.id)
            return {'value': {'city': city.name,
                'state_id': city.state_id.id,
                'country_id': city.country_id and city.country_id.id or False}}
        return {}

    @api.onchange('state_id')
    def onchange_state_city(self):
        if self.city_id and self.state_id and self.env['res.country.state.city'].browse(self.city_id.id).state_id != self.state_id:
            self.write({'city':None,'city_id':None})
