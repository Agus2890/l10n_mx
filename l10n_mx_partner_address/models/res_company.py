# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo import SUPERUSER_ID


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _compute_address(self):
        for company in self.filtered(lambda company: company.partner_id):
            address_data = company.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = company.partner_id.browse(address_data['contact']).sudo()
                company.street = partner.street
                company.street2 = partner.street2
                company.city = partner.city
                company.zip = partner.zip
                company.state_id = partner.state_id
                company.country_id = partner.country_id
                #company.fax = partner.fax
                company.l10n_mx_street3 = partner.l10n_mx_street3
                company.l10n_mx_street4 = partner.l10n_mx_street4
                company.l10n_mx_city2 = partner.l10n_mx_city2

    def _inverse_l10n_mx_address(self):
        for company in self:
            company.partner_id.l10n_mx_street3 = company.l10n_mx_street3
            company.partner_id.l10n_mx_street4 = company.l10n_mx_street4
            company.partner_id.l10n_mx_city2 = company.l10n_mx_city2

    l10n_mx_street3 = fields.Char(compute='_compute_address', inverse=_inverse_l10n_mx_address, size=128, string="No. External", multi='address', help='External number of the partner address')
    l10n_mx_street4 = fields.Char(compute='_compute_address', inverse=_inverse_l10n_mx_address, size=128, string="No. Internal", multi='address', help='Internal number of the partner address')
    l10n_mx_city2 = fields.Char(compute='_compute_address', inverse=_inverse_l10n_mx_address, size=128, string="Locality", multi='address', help='Locality configurated for this partner')
