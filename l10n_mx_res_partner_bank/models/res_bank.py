# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _get_take_digits(self):
        result = {}
        res = ''
        n = -1
        for last in self:
            for digit in last.acc_number[::-1]:
                if(digit.isdigit() == True) and len(res) < 4:
                    res = digit + res
            result[last.id] = res
        return result
    
#     clabe = fields.Char('Clabe Interbancaria', size=64, required=False)
    last_acc_number = fields.Char(compute='_get_take_digits', string="Ultimos 4 digitos", size=4, store=True)
#     # currency2_id = fields.Many2one('res.currency', string='Currency')
    reference = fields.Char('Reference', size=64, help='Reference used in this bank')
