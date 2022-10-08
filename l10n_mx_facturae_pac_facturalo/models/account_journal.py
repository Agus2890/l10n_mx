# -*- encoding: utf-8 -*-
##############################################################################
#    Module Writen to Odoo, Open Source Management Solution
#    All Rights Reserved.
#    info@mikrointeracciones.com.mx
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

from odoo import fields, models


class account_journal(models.Model):
    _inherit = 'account.journal'

    type_cfdi = fields.Selection(
        selection_add=[('cfdi_pac_xpd', 'CFDI 4.0 Expide tu factura')]
    )