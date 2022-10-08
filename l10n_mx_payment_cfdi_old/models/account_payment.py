# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
# import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.translate import _
from odoo import tools, netsvc

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from pytz import timezone
import pytz

#
import base64
#import StringIO
from io import StringIO
import string
import qrcode
import tempfile
import os
from odoo import SUPERUSER_ID


# class MailTemplatePayment(models.Model):
#     _inherit = "mail.template"

#     @api.multi
#     def generate_email(self, res_ids, fields=None):
#         res=super(MailTemplatePayment, self).generate_email(res_ids,fields=fields)
#         if isinstance(res,  dict) and type(res_ids) is not int:
#             if res[res_ids[0]]['model']=='account.payment':
#                 states = ['printable', 'sent_customer', 'done']
#                 att_obj = self.env['ir.attachment.payment.mx']
#                 iatt_ids = att_obj.search([('payment_id', '=', res_ids[0])])
#                 for iattach in iatt_ids:
#                     attachments = []
#                     if iattach.state in states:
#                         attachments.append(iattach.file_xml_sign.id)
#                         attachments.append(iattach.file_pdf.id)
#                         res[res_ids[0]]['attachment_ids'] = attachments
#         return res


# class AccountAbstractPayment(models.AbstractModel):
#     _inherit = "account.abstract.payment"

#     invoice_lines = fields.One2many('payment.invoice.line', 'payment_id', 'Invoices',
#         help='Please select invoices for this partner for the payment')
#     selected_inv_total = fields.Float(compute='compute_selected_invoice_total',
#         store=True, string='Assigned Amount')
#     balance = fields.Float(compute='_compute_balance', string='Balance')


# class PaymentInvoiceLine(models.Model):
#     _name = 'payment.invoice.line'

#     invoice_id = fields.Many2one('account.invoice', 'Invoice')
#     payment_id = fields.Many2one('account.payment', 'Related Payment')
#     partner_id = fields.Many2one(related='invoice_id.partner_id', string='Partner')
#     amount_total = fields.Monetary('Amount Total')
#     residual = fields.Monetary('Amount Due')
#     amount = fields.Monetary('Amount To Pay',
#         help="Enter amount to pay for this invoice, supports partial payment")
#     actual_amount = fields.Float(compute='compute_actual_amount',
#                                  string='Actual amount paid',
#                                  help="Actual amount paid in journal currency")
#     date_invoice = fields.Date(related='invoice_id.date_invoice', string='Invoice Date')
#     currency_id = fields.Many2one(related='invoice_id.currency_id', string='Currency')

#     @api.multi
#     @api.depends('amount', 'payment_id.payment_date')
#     def compute_actual_amount(self):
#         for line in self:
#             if line.amount > 0:
#                 line.actual_amount = \
#                     line.currency_id.with_context(date=line.payment_id.payment_date).compute(
#                         line.amount, line.payment_id.currency_id)
#             else:
#                 line.actual_amount = 0.0

#     @api.multi
#     @api.constrains('amount')
#     def _check_amount(self):
#         for line in self:
#             if line.amount < 0:
#                 raise UserError(_('Amount to pay can not be less than 0! (Invoice code: %s)')
#                     % line.invoice_id.number)
#             if line.amount > line.residual:
#                 raise UserError(_('"Amount to pay" can not be greater than than "Amount '
#                                   'Due" ! (Invoice code: %s)')
#                                 % line.invoice_id.number)

#     @api.onchange('invoice_id')
#     def onchange_invoice(self):
#         if self.invoice_id:
#             self.amount_total = self.invoice_id.amount_total
#             self.residual = self.invoice_id.residual
#         else:
#             self.amount_total = 0.0
#             self.residual = 0.0


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    

        
    # @api.multi
    # def cancel_complement(self):
    #     if self.payment_type == 'inbound':
    #         att_ids=self.env['ir.attachment.payment.mx'].search([('payment_id','=',self.id),('state','not in',['cancel', 'draft'])])
    #         for at in att_ids:
    #             if at.state != 'cancel':
    #                 at.signal_cancel_payment()
   

    # @api.multi
    # def action_payment_send(self):
    #     assert len(self) == 1, 'This option should only be used for a single id at a time.'
    #     template = self.env.ref('l10n_mx_payment_cfdi.email_template_template_payment_mx', False)
    #     compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
    #     ctx = dict(
    #         default_model='account.payment',
    #         default_res_id=self.id,
    #         default_use_template=bool(template),
    #         default_template_id=template and template.id or False,
    #         default_composition_mode='comment',
    #         mark_invoice_as_sent=True,
    #     )
    #     return {
    #         'name': _('Compose Email'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form.id, 'form')],
    #         'view_id': compose_form.id,
    #         'target': 'new',
    #         'context': ctx,
    #         }

    # def action_send_customer_force(self):
    #     email_act=self.action_payment_send()
    #     email_ctx = email_act['context']
    #     self.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
    #     return True

    # def create_report(
    #     self, cr, uid, res_ids, report_name=False,
    #     file_name=False, context=None
    # ):

    #     if context is None:
    #             context = {}
    #     if not report_name or not res_ids:
    #         return (False, Exception('Report name and Resources ids are required !!!'))
    #     ret_file_name = file_name + '.pdf'
    #     service = netsvc.LocalService("report." + report_name)
    #     (result, format) = service.create(cr, SUPERUSER_ID, res_ids, report_name, context=context)
    #     fp = open(ret_file_name, 'wb+')
    #     fp.write(result)
    #     fp.close()
    #     return (True, ret_file_name)

    # def get_qrcode(self, payment):
    #     tt = string.zfill('%.6f' % payment.amount, 17)
    #     qr = qrcode.QRCode(version=4, box_size=4, border=1)
    #     qr.add_data('?re=' + payment.company_id.partner_id.vat_split or payment.company_id.partner_id.vat)
    #     qr.add_data('&rr=' + payment.partner_id.vat_split or payment.company_id.vat)
    #     qr.add_data('&tt=' + tt)
    #     qr.add_data('&id=' + payment.cfdi_folio_fiscal)
    #     qr.make(fit=True)
    #     img = qr.make_image()
    #     output = StringIO.StringIO()
    #     img.save(output, 'PNG')
    #     output_s = output.getvalue()
    #     return base64.b64encode(output_s)

    def get_serie(self):
        serie=False
        folio=False
        if self.name:
            serie=self.journal_id.code
            folio=self.name.replace(self.journal_id.code,'')
            # journal_sequence, domain=self._get_seq_number_next_stuff()
            # serie, dummy = journal_sequence._get_prefix_suffix()
            # folio=self.number[len(serie):] if serie else False
        return (serie,folio)

    def get_currency_rate(self,currency_id=None):
        rate=1
        if currency_id:
            #currency_id=self.env['res.currency'].browse(currency_id)
            #raise UserError( str( currency_id ))
            rate = currency_id._convert(1, self.company_id.currency_id, self.company_id,self.date or fields.Date.context_today(self),round=False)
        elif self.journal_id.currency_id and self.journal_id.currency_id.id!=self.company_id.currency_id.id:
            rate =self.journal_id.currency_id._convert(1, self.company_id.currency_id, self.company_id,self.date or fields.Date.context_today(self),round=False)
        return rate


    payment_datetime = fields.Datetime(
        'Fecha timbrado CFDI',
        copy=False, help='Date of electronic payment',
        default=fields.Datetime.now,
        #default=fields.Date.context_today
    )
    rfcprovcertif = fields.Char(
        'RfcProvCertif', size=64, copy=False)
    no_certificado = fields.Char(
        'No. Certificate',
        size=64,
        copy=False,
        help='Number of serie of certificate used for the invoice'
    )
    certificado = fields.Text(
        'Certificate', size=64, copy=False,
        help='Certificate used in the invoice'
    )
    sello = fields.Text('Stamp', size=512, copy=False, help='Digital Stamp')#
    cadena_original = fields.Text(
        'String Original', size=512, copy=False,
        help='Data stream with the information contained in the electronic'
        ' invoice'
    )
    cfdi_xml=fields.Binary('XML TIMBRADO')

    cfdi_fecha_timbrado = fields.Datetime(
        'CFD-I Date Stamping', copy=False,
        help='Date when is stamped the electronic invoice'
    )
    cfdi_fecha_cancelacion = fields.Datetime(
        'CFD-I Date Cancel', copy=False
    )
    cfdi_folio_fiscal = fields.Char(
        'CFD-I Folio Fiscal', size=64, copy=False,
        help='Folio used in the electronic invoice'
    )
    cfdi_sello = fields.Text(
        'CFD-I Stamp', copy=False, help='Sign assigned by the SAT'
    )
    cfdi_cadena_original = fields.Text(
        'CFD-I Original String', copy=False,
        help='Original String used in the electronic invoice'
    )
    cfdi_no_certificado = fields.Char(
        'CFD-I Certificado', size=32,
        help='Serial Number of the Certificate'
    )
    date_payment_tz = fields.Datetime(
        'Date Invoiced with TZ'
    )
    cfdi_qrcode = fields.Binary(
        'QRCode'
    )
    replace_cfdi_sat = fields.Boolean(
        string="¿Este CFDI sustituye otro CFDI?", copy=False
    )
    type_relation = fields.Selection([
        # ('01','01-Nota de crédito de los documentos relacionados'),        
        # ('02','02-Nota de débito de los documentos relacionados'),
        # ('03','03-Devolución de mercancía sobre facturas o traslados previos'),
        ('04','04-Sustitución de los CFDI previos'),
        # ('05','05-Traslados de mercancias facturados previamente'),
        # ('06','06-Factura generada por los traslados previos'),
        # ('07','07-CFDI por aplicación de anticipo')
        ], 
        string='Tipo Relacion', copy=False
    )
    relation_ids = fields.Many2many('ir.attachment.payment.mx', 
        'ir_attachment_payment_relation', 'payment_relation_id', 'payment_id', 
        string="Complemento Relacionado", copy=False
    )
    payment_type_id=fields.Many2one("payment.type",string="Forma de Pago")
    payment_rate = fields.Float('Tipo de Cambio', digits=(12,6))


    def get_filename(self):
        filename=str(self.company_id.partner_id.vat_split)+'_'
        filename+=self.name
        return filename

    def action_cfdi_attachment(self):
        # currency_usd=self.env['res.currency'].browse(2)
        #rate=self.get_currency_rate()
        if not self.payment_type_id:
            raise UserError("Ingrese la forma de Pago")
        return self.create_ir_attachment_payment()
        # pay_term_lines = self.move_id.line_ids\
        #     .filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))
        # for partial in pay_term_lines.matched_debit_ids:
        #     raise UserError( str( partial ))
        # return True

    def action_post(self):
        res = super(AccountPayment,self).action_post()
        for rec in self:
            if rec.cfdi_folio_fiscal!=False:
                continue 
            # if rec.payment_type == 'inbound' and rec.partner_type=='customer':
                #for line in rec.move_line_ids:
                raise ValidationError( str(  res.move_id.line_ids.full_reconcile_id ))
        return res

    def create_ir_attachment_payment(self):#receipt
        ir_attach_obj = self.env['ir.attachment.payment.mx']
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        move_ids=[]
        invoice_ids=[]
        attach_ids=[]
        ###
        pay_term_lines = self.move_id.line_ids\
            .filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))
        
        # for line in self.move_id.line_id:
        #     if line.reconciled == True:
        #         line = self.env['account.partial.reconcile'].search([('credit_move_id', '=', line.id)])

        for partial in pay_term_lines.matched_debit_ids:
            # raise UserError( str(  ))
            if partial.debit_move_id.move_id:
                # raise UserError( str(  partial.debit_move_id.move_id.invoice_payments_widget  ))
                #len(rec.debit_move_id.invoice_id.invoice_payments_widget )
                partial.write({
                    'sequence':len(partial.debit_move_id.move_id._get_reconciled_invoices_partials()),
                    'amount_residual_cfdi':partial.debit_move_id.move_id.amount_residual
                })
                move_ids.append(partial.id)
                invoice_ids.append(partial.debit_move_id.move_id.id)
        if not move_ids:
            raise UserError(str("El pago no esta relacionado a  una factura.")) 
        number = len(invoice_ids)
        if invoice_ids:
            invoice_obj = self.env['account.move'].browse(invoice_ids[0])
            if self.payment_type == 'inbound':
                # raise UserError( str( self))
                if invoice_obj.journal_id.sign_sat: 
                    att_id = False
                    # raise UserError( str( att_id ))
                    for att_id_ids in ir_attach_obj.sudo().search([('payment_id','=', self.id),('state','=','draft')],limit=1):
                        if att_id_ids:
                            attach_ids.append(att_id_ids.id)
                    if not att_id and attach_ids == []:
                        att_id = ir_attach_obj.create({
                                    'name': self.get_filename(),
                                    'payment_id': self.id,
                                    'payment_ids':[(6,0,move_ids)],
                                    'invoice_id': invoice_ids[0] if number==1 else False,
                                    'invoice_ids': [(6,0,invoice_ids)] if number>1 else [(6,0,[])],
                                    'state': 'draft',
                                    'type':invoice_obj.journal_id.type_cfdi if number==1 else False,
                                    'company_id': self.company_id.id,
                            })
                        attach_ids.append(att_id.id)
            if attach_ids:
                # result = act_obj.for_xml_id('l10n_mx_payment_cfdi','action_ir_attachment_payment_mx')
                # result = self.env.ref('l10n_mx_payment_cfdi.action_ir_attachment_payment_mx').read()
                # raise UserError( str( result ))
                # result['domain'] = "[('id','in',[" + ','.join(map(
                #     str, attach_ids)) + "])]"
                # result['res_id'] = attach_ids and attach_ids[0] or False
                # res = mod_obj.get_object_reference('l10n_mx_payment_cfdi',
                #     'view_ir_attachment_payment_mx_form')
                # result['views'] = [(res and res[1] or False, 'form')]

                # return result   
                # raise UserError( str( "p"))
                return {
                    'name': self.name,
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'ir.attachment.payment.mx',
                    'res_id': attach_ids[0],
                }   
        return True