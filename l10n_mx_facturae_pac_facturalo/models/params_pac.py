# -*- encoding: utf-8 -*-
##############################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2008 MKI
#    All Rights Reserved.
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _


class ParamsPac(models.Model):
    _inherit = 'params.pac'

    def _get_method_type_selection(self):
        types = super(ParamsPac, self)._get_method_type_selection()
        types.extend([
            ('pac_xpd_cancelar', _('PAC xpd - Cancel')),
            ('pac_xpd_firmar', _('PAC xpd - Sign')),
        ])
        return types

    method_type = fields.Selection('_get_method_type_selection',
        "Process to perform", size=64, required=True,
        help='Type of process to configure in this pac')
