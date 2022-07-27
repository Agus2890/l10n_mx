# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import tools


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_invoice_certificate(self, field_names=None, arg=False):
        context = dict(self._context or {})
        company_obj = self.env['res.company']
        certificate_obj = self.env['res.company.facturae.certificate']
        res = {}
        for invoice in self:
            # Translate context into normal dictionary for V8 compat
            context = {}
            context.update({'date_work': invoice.date_invoice})
            certificate_id = False
            certificate_id = company_obj._get_current_certificate()
            certificate_id = certificate_id and certificate_obj.browse([certificate_id])[0] or False
            res[invoice.id] = certificate_id and certificate_id.id or False
        return res

    certificate_id = fields.Many2one('res.company.facturae.certificate',
    		compute='_get_invoice_certificate', method=True,
            string='Invoice Certificate', store=True,
            help='Id of the certificate used for the invoice'),
