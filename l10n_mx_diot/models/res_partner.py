# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'


    type_of_third = fields.Selection([
        ('04', '04 - National Supplier'),
        ('05', '05 - Foreign Supplier'),
        ('15', '15 - Global Supplier')],
        'Type of Third (DIOT)', help=_('Type of third for this partner'))

    type_of_operation = fields.Selection([
        ('03', '03 - Professional Services'),
        ('06', '06 - Building Rental'),
        ('85', '85 - Others')],
        'Type of Operation (DIOT)')

    nacionality_diot = fields.Char(_('Nacionality'), size=100,
                            help=_('Type nacionality when foreign supplier'))
