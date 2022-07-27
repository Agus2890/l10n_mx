# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
       
    payment_type_customer_id = fields.Many2one(
        'payment.type', string='Forma de Pago',
        help="Payment type of the customer"
    )
    # payment_type_supplier_id = fields.Many2one(
    #     'payment.type', string='Supplier Payment Type',
    #     help="Payment type of the supplier"
    # )
