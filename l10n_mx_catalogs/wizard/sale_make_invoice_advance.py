# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        #res.invoice_line_ids._onchange_product_id()
        for inv in res:
            for line in inv.invoice_line_ids:
                line.write({'code_product_sat':line.product_id.product_tmpl_id.code_product_sat and line.product_id.product_tmpl_id.code_product_sat.id or \
                line.product_id.product_tmpl_id.categ_id.code_product_sat.id})
                line.write({'product_unit_sat':line.product_id.product_tmpl_id.product_unit_sat and line.product_id.product_tmpl_id.product_unit_sat.id or \
                line.product_id.product_tmpl_id.categ_id.product_unit_sat.id
                })
        return res
        
class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        res=super(AccountMoveReversal,self).reverse_moves()
        if res and res.get('res_id',False):
            move_id=self.env['account.move'].browse(self.env.context.get('active_id'))
            new_move_id=self.env['account.move'].browse(res.get('res_id',False))
            new_move_id.write({
                'type_relation':self.type_relation,
                'relation_ids':[(6,0,[self.env.context.get('active_id')])]
            })
            if not self.amount_nc:
                raise UserError(str("Indique el importe para la nota de credito"))
            if self.type_relation in ['01','03','07']:
                porcent=str(int((self.amount_nc*100)/move_id.amount_total))+"%"
                
                name=False
                if self.type_relation == '01':
                    name=("""%s descuento de los CFDI relacionados, Factura %s acreditada""")%(porcent, move_id.name) 
                elif self.type_relation=='03':
                    name=("""Devolución de los CFDI relacionados, Factura %s acreditada""")%(move_id.name)
                elif self.type_relation=='07':
                    name=("""Aplicación de anticipo""")

                clave=self.env['key.product.sat'].search([('code_sat','=','84111506')])
                unidad=self.env['key.unit.sat'].search([('code_sat','=','ACT')])
                udm=self.env['uom.uom'].search([('name','=','No Aplica')])
                tax_ids= new_move_id.invoice_line_ids[0].tax_ids
                #raise UserError( str( new_move_id.invoice_line_ids[0].tax_ids  ))
                new_move_id.line_ids.unlink()
                new_move_id.invoice_line_ids=[(0,0,{'name':name,'price_unit':self.amount_nc,'quantity':1,'code_product_sat':clave.id,
                    'product_unit_sat':unidad.id,'product_uom_id':udm.id,'product_id':False,'tax_ids':[(6,0,tax_ids.ids)]})]
        return res

    type_relation = fields.Selection(
            [('01','01-Nota de crédito de los documentos relacionados'),        
            #('02','02-Nota de débito de los documentos relacionados'),
            ('03','03-Devolución de mercancía sobre facturas o traslados previos'),
            ('04','04-Sustitución de los CFDI previos'),
            #('05','05-Traslados de mercancias facturados previamente'),
            #('06','06-Factura generada por los traslados previos'),
            ('07','07-CFDI por aplicación de anticipo')], 
            string='Tipo Relacion', copy=False,default='01'
        )
    amount_nc=fields.Float(string="Importe NC")

    

    