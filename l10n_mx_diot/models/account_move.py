# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class AccountMove(models.Model):
    _inherit = "account.move"

    use_in_diot = fields.Boolean(
        'Use in DIOT',help='Unset if you do not want to include this movement into'' DIOT report')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    use_in_diot = fields.Boolean(related='move_id.use_in_diot',  store=False, string="Use in DIOT")

    # @api.model
    # def create(self,vals):
    #     """
    #     Check the partner and set default value for column use in diot
    #     according to partner information
    #     """
    #     partner_obj = self.env['res.partner']
    #     # Prevent fail when no partner asigned to movement
    #     if 'partner_id' in vals and vals['partner_id']:
    #         partner = partner_obj.browse(vals['partner_id'])
    #         if partner.vat_subjected:
    #             acc_mov_obj = self.env['account.move']
    #             acc_mov = acc_mov_obj.browse(vals['move_id'])
    #             if not acc_mov.use_in_diot:
    #                 acc_mov_obj.write([acc_mov.id],{'use_in_diot': True})
    #     return super(AccountMoveLine, self).create(vals)
