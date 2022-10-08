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
from io import StringIO,BytesIO


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def get_qrcode(self):
        """Genera el código de barras bidimensional para una factura
            @param invoice: Objeto invoice con los datos de la factura

            @return: Imagen del código de barras o None
        """
        output_s=False
        for inv in self: 
            # Procesar invoice para obtener el total con 17 posiciones
            tt = str.zfill('%.6f' % inv.amount, 17)
            ## Procesar invoice para obtener los ocho últimos caracteres del sello digital del emisor del comprobante.
            fe = inv.sello[-8:]
            # Init qr code
            qr = qrcode.QRCode(version=4, box_size=4, border=1)
            qr.add_data('https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=' + inv.company_id.partner_id.vat or inv.company_id.partner_id.vat)        
            qr.add_data('&id=' + inv.cfdi_folio_fiscal)              
            qr.add_data('&rr=' + inv.partner_id.vat or inv.company_id.vat)
            qr.add_data('&tt=' + tt)
            qr.add_data('&fe=' + fe)
            qr.make(fit=True)
            img = qr.make_image()
            output = BytesIO()
            img.save(output,'PNG')
            output_s = output.getvalue()
        return base64.b64encode(output_s)


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
    payment_rate = fields.Float('Tipo de Cambio', digits=(12,4))


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
                        att_id.action_update()
                        currency_credit=att_id.payment_ids.filtered(lambda x:x.debit_currency_id!=x.company_currency_id or x.credit_currency_id !=x.company_currency_id)
                        if currency_credit and not self.payment_rate:
                            rate=self.get_currency_rate(currency_credit[0].debit_currency_id if  currency_credit[0].credit_currency_id==currency_credit[0].company_currency_id else currency_credit[0].credit_currency_id)
                            #raise UserError(str( rate))
                            self.write({'payment_rate':round(rate,4) })
                        elif not currency_credit and not self.payment_rate:
                            self.write({'payment_rate':1 })

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