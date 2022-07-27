# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class CifConfig(models.TransientModel):
    _name = 'cif.config'
    _inherit = 'res.config'

    cif_file = fields.Binary('CIF', help="Fiscal Identification Card")

    # def _write_company(self, cr, uid, cif_file, company_id, context=None):
    #     self.pool.get('res.company').write(cr, uid, company_id, {
    #         'cif_file': cif_file,
    #     }, context=context)

    # def execute(self):
    #     companies = self.env['res.company'].sudo().search([('partner_id','=',self.create_uid.id)])

    #     cif = self.cif_file
    #     if cif:
    #         for company in companies:
    #             company.sudo().write({
    #                 'cif_file': cif,
    #             })


