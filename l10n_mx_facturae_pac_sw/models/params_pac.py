# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _


class ParamsPac(models.Model):
    _inherit = 'params.pac'

    @api.model
    def _get_method_type_selection(self):
        types = super(ParamsPac, self)._get_method_type_selection()
        types.extend([
            ('pac_sw_cancelar', _('PAC SW Sapien - Cancel')),
            ('pac_sw_firmar', _('PAC SW Sapien - Sign')),
        ])
        return types

    method_type = fields.Selection('_get_method_type_selection',
        "Process to perform", size=64, required=True,
        help='Type of process to configure in this pac')

