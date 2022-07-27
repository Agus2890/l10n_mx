# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Account_Journal(models.Model):
    _inherit = 'account.journal'

    def _get_type(self):
        types = []
        return types

    # def copy(self, default={}, done_list=[], local=False):
    #     if not default:
    #         default = {}
    #     default = default.copy()
    #     default['type'] = False
    #     return super(account_journal, self).copy(default)

    type_cfdi = fields.Selection(
            [], string='Type CFDI', size=64, help="Type of CFDI"
        )

    sign_sat = fields.Boolean(
            'Sign SAT',
            help="If this field is enabled, then sign through the"
            " webservice of the Mexican SAT"
        )
