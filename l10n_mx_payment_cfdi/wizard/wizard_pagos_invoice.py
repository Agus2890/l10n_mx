# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, RedirectWarning


class PagosInvoiceSat(models.TransientModel):
    _name = 'pagos.invoice.sat'

    @api.model
    def default_get(self, fields):
        res = super(PagosInvoiceSat, self).default_get(fields)
        invoice_obj = self.env['account.invoice'].browse(self._context.get('active_id'))
        #active_model = self._context.get('active_model')
        #'name':active_model,
        pagos=[(6,0,[r.id for r in invoice_obj.payment_ids])]
        res.update({'payment_ids':pagos})
        return res
        
    name=fields.Char(string='Nombre')
    payment_ids=fields.Many2many('account.move.line',string="Lineas de Pago",readonly=True)