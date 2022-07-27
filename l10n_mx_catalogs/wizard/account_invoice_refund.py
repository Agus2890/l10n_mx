# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# import time

# from openerp.osv import fields, osv
# from openerp.tools.translate import _
# from openerp.tools.safe_eval import safe_eval as eval
from odoo import api, fields, models, _
from odoo.exceptions import UserError


# class account_invoice_refund(models.TransientModel):
#     _inherit = "account.invoice.refund"

#     type_relation=fields.Selection([
#             ('01','01-Nota de crédito de los documentos relacionados'),
#             ('02','02-Nota de débito de los documentos relacionados'),
#             ('03','03-Devolución de mercancía sobre facturas o traslados previos'),
#             ('04','04-Sustitución de los CFDI previos'),
#             ('05','05-Traslados de mercancias facturados previamente'),
#             ('06','06-Factura generada por los traslados previos'),
#             ('07','07-CFDI por aplicación de anticipo')
#             ],string='Tipo Relacion',required=True,default="01")


#     def compute_refund(self, mode='refund'):
#         result=super(account_invoice_refund,self).compute_refund(mode=mode)
#         #for k in result['domain']:
#         lista=list(result['domain'])
#         #raise UserError( str( lista[1][2] ))
#         #if lista[2]=='id':
#         inv_obj=self.env['account.invoice']
#         inv_id=inv_obj.browse(self.env.context.get('active_id'))
#         inv_refund_id=inv_obj.browse( lista[1][2] )
#         inv_refund_id.write({
#            'relation_ids':[(0,0,{'id_invoice':inv_id.id})],
#            'usocfdi_id':inv_id.usocfdi_id.id,
#            'payment_type_id':inv_id.payment_type_id.id,
#            'partner_bank_id':inv_id.partner_bank_id.id,
#            'type_relation':'01'
#            })
#         return result