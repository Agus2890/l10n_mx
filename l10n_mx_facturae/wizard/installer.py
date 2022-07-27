# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class FacturaeConfig(models.TransientModel):
    _name = 'facturae.config'
    _inherit = 'res.config'
    _description = __doc__

    def _assign_vat(self, vat, company_id):
        """
        @param vat : VAT that will be set in the company
        @param company_id : Id from the company that the user works
        """
        partner_id = self.env['res.company'].browse(company_id).partner_id.id
        partner_obj = self.env['res.partner']
        if partner_obj.check_vat():
            partner_obj.write(partner_id, {
                'vat': vat,
            })

    def execute(self):
        ids = isinstance(int, long)
        company_id = self.env['res.users'].browse().company_id.partner_id.id
        wiz_data = self.read(ids)
        if wiz_data[0]['vat']:
            self._assign_vat(wiz_data[0]["vat"], company_id)

    vat = fields.Char('VAT', size=64, help='Federal Register of Causes')
    company_id = fields.Many2one('res.company', 'Company',
        help="Select company to assing vat and/or cif")

