# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)

# class ResPartner(models.Model):
#     _inherit = 'res.partner'
#     account_anticipo_id=fields.Many2one("account.account",string="Cuenta Anticipo")

class AccountMove(models.Model):
    _inherit = 'account.move'

    # def _get_last_sequence(self,lock=False):
    #     res=super(AccountMove,self)._get_last_sequence(lock=lock)
    #     if self.move_type=='out_invoice':
    #         res='I'+res
    #     elif self.move_type=='out_refund':
    #         res='E'+res
    #     return res

    # def create(self, vals_list):
    #     res=super(AccountMove,self).create(vals_list)
    #     raise UserError( str( res.name ))
    #     return res


    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        res=super(AccountMove,self)._recompute_dynamic_lines(recompute_all_taxes=recompute_all_taxes, recompute_tax_base_amount=recompute_tax_base_amount)
        if self.line_ids and self.anticipo:
            tax_credit=self.line_ids.filtered(lambda x:x.tax_tag_ids and x.credit>0)
            tax_debit=self.line_ids.filtered(lambda x:x.tax_tag_ids and x.debit>0)
            if not tax_debit:
                raise UserError( str( tax_credit.read().credit )) 
        return res

    def _compute_amount_residual(self):
        for line in self:
            if line.journal_id.type=='sale' and line.move_type=='entry':
                move_line=line.line_ids.filtered(lambda x: x.account_id.user_type_id.type in ('receivable'))
                line.amount_anticipo=abs( move_line.amount_residual )
            else:
                line.amount_anticipo=0

    @api.onchange('type_relation')
    def onchange_type_relation(self):
        if self.move_type=='out_invoice' and self.type_relation=='07':
            move_ids=self.env['account.move'].search([('state','not in',['cancel','draft']),('anticipo','=',True),('partner_id','=',self.partner_id.id),('move_type','=','entry'),('company_id', '=', self.company_id.id)])
            data=[]
            for line in move_ids.mapped('line_ids').filtered(lambda x: x.account_id.user_type_id.type in ('receivable')):
                if abs( line.amount_residual ):
                    data.append(line.move_id.id)
            return {'domain':{'relation_ids': [('id','in',data)]}}
        else:
            return {'domain':{'relation_ids': [('state','!=','draft'),('partner_id','=',self.partner_id.id),('move_type','=','out_invoice'),('company_id', '=',self.company_id.id)]}}



    usocfdi_id = fields.Many2one(
            'uso.cfdi', string='Uso CFDI', readonly=True, 
            states={'draft': [('readonly', False)]}
        )
    payment_method = fields.Selection(
            [('PUE','Pago en una sola exhibicion'),('PPD','Pago en parcialidades o diferido')], 
            string='Metodo de Pago', default="PUE", copy=False, readonly=True, states={'draft': [('readonly', False)]}
        )
    replace_cfdi_sat = fields.Boolean(
            string="¿Este CFDI sustituye otro CFDI?", copy=False
        )
    type_relation = fields.Selection(
            [('01','01-Nota de crédito de los documentos relacionados'),        
            ('02','02-Nota de débito de los documentos relacionados'),
            ('03','03-Devolución de mercancía sobre facturas o traslados previos'),
            ('04','04-Sustitución de los CFDI previos'),
            ('05','05-Traslados de mercancias facturados previamente'),
            ('06','06-Factura generada por los traslados previos'),
            ('07','07-CFDI por aplicación de anticipo')], 
            string='Tipo Relacion', readonly=True, copy=False, states={'draft': [('readonly', False)]}
        )

    
    relation_ids = fields.Many2many('account.move', 
            'account_move_relation', 'move_relation_id', 'move_id', 
            string="Factura Relacionada", readonly=True, states={'draft': [('readonly', False)]}
        )
    relation_anticipo_ids = fields.Many2many('account.move', 
            'account_move_anticipo_relation', 'move_relation_id', 'move_id', 
            string="Factura Relacionada Ant", readonly=True, states={'draft': [('readonly', False)]}
        )
    anticipo=fields.Boolean(string="Anticipo")
    amount_anticipo=fields.Float(compute='_compute_amount_residual',string="Saldo Anticipo",store=True)






#     def action_date_assign(self):
#         res=super(AccountInvoice,self).action_date_assign()
#         if self.journal_id.sign_sat and self.state not in ['proforma','proforma2']:
#             if not self.partner_id.vat:
#                 raise UserError(_('El cliente no cuenta con un "RFC"'))
#             if not self.usocfdi_id:
#                raise UserError(_('Indique el "Uso de CFDI" para la factura'))
#             if not self.payment_type_id:
#                raise UserError(_('Indique "Forma de pago" para la factura'))
#             if not self.paymethod:
#                raise UserError(_('Indique Metodo de pago" para la factura'))
#             for line in self.invoice_line_ids:
#                 if not line.code_product_sat:
#                     raise UserError(_('Indique "Codigo del SAT" para %s') % (line.name))
#                 if not line.product_unit_sat:
#                     raise UserError(_('Indique "Unidad del SAT" para %s') % (line.name))
#                 if not line.invoice_line_tax_ids:
#                     raise UserError(_('Se debe indicar un "Impuesto" para el producto %s') % (line.name))
#         return res

    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # def _prepare_invoice(self):
    #     res=super(SaleOrderLine,self)._prepare_invoice()
    #     if res:
    #         res.update({'code_product_sat':line.code_product_sat.id,'product_unit_sat':line.product_unit_sat.id})
    #     return res

    def _prepare_invoice_line(self, **optional_values):
        res=super(SaleOrderLine,self)._prepare_invoice_line(**optional_values)
        if res:
            # res.update({'code_product_sat':self.code_product_sat.id,'product_unit_sat':self.product_unit_sat.id})
            res.update({'code_product_sat':self.product_id.code_product_sat.id,'product_unit_sat':self.product_id.product_unit_sat.id})
        return res

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.code_product_sat = self.product_id.product_tmpl_id.code_product_sat and self.product_id.product_tmpl_id.code_product_sat.id or \
                self.product_id.product_tmpl_id.categ_id.code_product_sat.id
            self.product_unit_sat = self.product_id.product_tmpl_id.product_unit_sat and self.product_id.product_tmpl_id.product_unit_sat.id or \
                self.product_id.product_tmpl_id.categ_id.product_unit_sat.id
        return res

    code_product_sat = fields.Many2one('key.product.sat', string='Clave Producto Sat')
    product_unit_sat = fields.Many2one('key.unit.sat', string='Clave Unidad Sat')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        for line in self:
            line.code_product_sat = line.product_id.product_tmpl_id.code_product_sat or False
            line.product_unit_sat = line.product_id.product_tmpl_id.product_unit_sat or False
        return res

    code_product_sat = fields.Many2one('key.product.sat',string='Clave Producto Sat')
    product_unit_sat = fields.Many2one('key.unit.sat',string='Clave Unidad Sat')   