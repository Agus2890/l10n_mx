# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api,fields
import time
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = 'account.move'



    # cfdi_folio_fiscal = fields.Char('CFD-I Folio Fiscal', size=64, help='Folio used in the electronic invoice')

    # @api.multi
    # def action_cancel(self):
    #     # First process the super
    #     super(AccountMove, self).action_cancel()
    #     attach_obj = self.env['ir.attachment.facturae.mx']
    #     inv_type_facturae = ['out_move', 'out_refund']
    #     for move in self:
    #         if move.type in inv_type_facturae:
    #             attach_ids = attach_obj.search([('move_id', '=', move.id)])
    #             for attach in attach_ids:
    #                 if attach.state != 'cancel':
    #                     attach_obj.signal_cancel()
    #     self.write(
    #         {'date_move_cancel': time.strftime('%Y-%m-%d %H:%M:%S')}
    #     )
    #     return

    # def action_post(self):
    #     res = super(AccountMove,self).action_post()
    #     return self.create_ir_attachment_facturae()
        #return res

    def action_generate_cfdi(self):
        if self.cfdi_folio_fiscal:
            raise UserError("Su factura ya fue timbrada previamente.")
        return self.create_ir_attachment_facturae()

    def create_ir_attachment_facturae(self):
        val=True#self.env['res.users'].has_group('l10n_mx_facturae_group_show_wizards.res_group_facturae_show_default_wizards')
        # self.ensure_one()
        ir_attach_obj = self.env['ir.attachment.facturae.mx']
        mod_obj = self.env['ir.model.data']
        # act_obj = self.env['ir.actions.act_window']
        attach_ids = False
        inv_type_facturae = {
            'out_move': True,
            'out_refund': True,
            'in_move': False,
            'out_invoice':True,
            'in_refund': False,
            'entry':True
            }
        for move in self:
            if inv_type_facturae.get(move.move_type, False):
                sign_sat = move.journal_id.sign_sat
                for attach in ir_attach_obj.search([('move_id', '=', move.id),('state', '=', 'draft')], limit=1):
                    if attach:
                        attach_ids = attach
                if sign_sat and attach_ids == False:
                    attach_ids = ir_attach_obj.create({
                        'name': move.fname_invoice,
                        'uuid': move.cfdi_folio_fiscal,
                        'move_id': move.id,
                        'type': move.journal_id.type_cfdi if move.journal_id.type_cfdi else False 
                        }
                    )
            # raise UserError("hola"+str(attach_ids))
        # if attach_ids and val==True:
        #     result = self.env.ref('l10n_mx_ir_attachment_facturae.action_ir_attachment_facturae_mx').read()[0]
        #     # result = act_obj.for_xml_id('l10n_mx_ir_attachment_facturae','action_ir_attachment_facturae_mx')
        #     # choose the view_mode accordingly
        #     result['domain'] = "[('id','in',["+str(attach_ids.id)+ "])]"
        #     result['res_id'] = attach_ids.id and attach_ids.id or False
        #     # res = mod_obj.get_object_reference(
        #     #     'l10n_mx_ir_attachment_facturae',
        #     #     'view_ir_attachment_facturae_mx_form')
        #     result['views'] = [(self.env.ref('l10n_mx_ir_attachment_facturae.view_ir_attachment_facturae_mx_form').id, 'form')]
        #     return result
        if attach_ids:
            attachment_id=attach_ids.action_sign()
            return True
        return True

