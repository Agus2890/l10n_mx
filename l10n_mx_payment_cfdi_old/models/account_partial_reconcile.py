# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, RedirectWarning
# import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'

#     # def _create_sequecen_cfdi(self, cr, uid, ids, r_id, context=None):
#     #     for line in self.browse(cr, uid, ids, context):
#     #         if not line.invoice.payment_ids:
#     #             continue
#     #         else:
#     #             #raise Warning("",str(line.invoice.payment_ids))
#     #             line.invoice.payment_ids.write({'invoice_id':line.invoice.id})
#     #         	r_id.write({'sequence':len([r.id for r in line.invoice.payment_ids if r.credit]),'invoice_id':line.invoice.id})

#     @api.multi
#     def _create_sequecen_cfdi(self, r_id):
#         for line in self:
#             if not line.invoice.payment_ids:
#                 continue
#             elif r_id[0]['partner_id']['customer'] == True:# else:   
#                 r_id = self.env['account.move.line'].search([('reconcile_id', '=', r_id[0]['reconcile_id']['id']),
#                     ('move_id', '=', r_id[0]['move_id']['id']), ('credit', '!=', 0), ('name', '=', '/')])
#                 r_id.write({'sequence':len(line.invoice.payment_ids.filtered(lambda x: x.credit != 0 and x.name != 'cambio: /' and x.name == '/'))
#                     ,'invoice_id':line.invoice.id})

#     def reconcile_partial(
#         self, cr, uid, ids, type='auto', context=None, writeoff_acc_id=False,
#         writeoff_period_id=False, writeoff_journal_id=False):
#         super(AccountMoveLine, self).reconcile_partial(
#             cr, uid, ids=ids,
#             type=type, writeoff_acc_id=writeoff_acc_id,
#             writeoff_period_id=writeoff_period_id,
#             writeoff_journal_id=writeoff_journal_id, context=context
#         )
#         acc_mov_line = self.browse(cr, uid, ids, context)[0]
#         if acc_mov_line.reconcile_partial_id:
#             self._create_sequecen_cfdi(cr, SUPERUSER_ID, ids, acc_mov_line, context=None)
#         return True

#     def reconcile(
#         self, cr, uid, ids, type='auto', writeoff_acc_id=False,
#         writeoff_period_id=False, writeoff_journal_id=False, context=None):
#         r_id = super(AccountMoveLine, self).reconcile(
#             cr, uid, ids=ids,
#             type=type, writeoff_acc_id=writeoff_acc_id,
#             writeoff_period_id=writeoff_period_id,
#             writeoff_journal_id=writeoff_journal_id, context=context
#         )
#         acc_mov_line = self.browse(cr, uid, ids, context)
#         res=[r.id for r in acc_mov_line if r.journal_id.type in ('cash', 'bank') ]
#         if res:
#             move_id=self.browse(cr, uid, max(res), context)
#             self._create_sequecen_cfdi(cr, SUPERUSER_ID,ids,move_id, context=None)


#     cfdi_folio_fiscal=fields.Char('CFD-I Folio Fiscal', size=100)
#     sequence=fields.Integer(string="N.Pago")
#     invoice_id=fields.Many2one('account.invoice',string="Factura")
#     amount_payment=fields.Float(string="Complemento", digits_compute=dp.get_precision('Account'))    


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    sequence = fields.Integer(string="N.Pago")
    amount_residual_cfdi = fields.Float( string='Saldo Pendiente')
    amount_residual_currency_cfdi = fields.Float(string='Saldo Pendiente USD')