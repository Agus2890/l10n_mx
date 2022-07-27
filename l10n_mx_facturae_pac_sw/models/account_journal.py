# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type_cfdi = fields.Selection(
        selection_add=[('cfdi32_pac_sw', 'CFDI 3.3 SW sapien')]
    )
