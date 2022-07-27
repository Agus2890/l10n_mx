# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
# from odoo.exceptions import UserError
# from odoo.tools import float_is_zero


# class AccountPartialReconcileCashBasis(models.Model):
#     _inherit = 'account.partial.reconcile'
    
    # def create_tax_cash_basis_entry(self, percentage_before_rec):
    #     res=super(AccountPartialReconcileCashBasis,self).create_tax_cash_basis_entry(percentage_before_rec)
    #     move_delete=False
    #     if self.credit_move_id.invoice_id:
    #         move_delete=self.debit_move_id.move_id
    #     elif self.debit_move_id.invoice_id:
    #         move_delete=self.credit_move_id.move_id
    #     if move_delete:
    #         move = self.env['account.move'].search([('ref','=',move_delete.name )], order='id desc', limit=1)
    #         move.button_cancel()
    #         for line in move.line_ids:
    #             self.env.cr.execute("UPDATE account_move_line set move_id=%s where id=%s",(move_delete.id,line.id))
    #         if move: 
    #             self.env.cr.execute("DELETE FROM account_move where id=%s",(move.id,))
    #     return res