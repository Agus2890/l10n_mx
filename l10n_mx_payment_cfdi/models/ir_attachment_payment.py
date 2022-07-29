# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import tools
from odoo import netsvc
from jinja2 import Environment, FileSystemLoader
import time
import tempfile
import base64
import codecs
# from unidecode import unidecode
import os
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from xml.dom.minidom import parse
import logging
_logger = logging.getLogger(__name__)
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz


class IrAttachmentPaymentMx(models.Model):
    _name = 'ir.attachment.payment.mx'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.model
    def _get_type(self):
        return []

    def get_driver_fc_sign(self):
        return {}

    def get_driver_fc_cancel(self):
        return {}

    name = fields.Char(string='Name', size=128, required=True, readonly=True)
    uuid = fields.Char(string='UUID', size=128, readonly=True)
    invoice_id = fields.Many2one('account.move', string='Factura', readonly=True)
    invoice_ids = fields.Many2many('account.move', string="Facturas", readonly=True)
    payment_id = fields.Many2one('account.payment', string='Payment', readonly=True)
    # payment_ids = fields.Many2many('account.move.line', string="Lineas de Pago",readonly=True)
    payment_ids = fields.Many2many('account.partial.reconcile', string="Lineas de Pago",readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    file_input = fields.Many2one('ir.attachment', 'File input',
            readonly=True, help='File input')
    type = fields.Selection('_get_type', string='Type')
    state = fields.Selection([
             ('draft', 'Draft'),
             ('confirmed', 'Confirmed'),
             ('signed', 'Signed'),
             ('printable', 'Printable Format Generated'),
             ('sent_customer', 'Sent Customer'),
             ('done', 'Done'),
             ('cancel', 'Cancelled'), ],
             string='State', readonly=True, required=True,default="draft", help='State of attachments')
    file_xml_sign = fields.Many2one('ir.attachment', string='File XML Sign',
            readonly=True, help='File XML signed')
    file_pdf = fields.Many2one('ir.attachment', string='File PDF', readonly=True,
            help='Report PDF generated for the electronic Invoice')
    last_date = fields.Datetime(
            string='Last Modified', readonly=True)
    description = fields.Text(string='Description')
    msj = fields.Text(string='Last Message', readonly=True,
            track_visibility='onchange',
            help='Message generated to upload XML to sign')
    
    def _get_certificate_str(self, fname_cer_pem=""):
        """
        @param fname_cer_pem : Path and name the file .pem
        """
        fcer = open(fname_cer_pem, "r")
        lines = fcer.readlines()
        fcer.close()
        cer_str = ""
        loading = False
        for line in lines:
            if 'END CERTIFICATE' in line:
                loading = False
            if loading:
                cer_str += line
            if 'BEGIN CERTIFICATE' in line:
                loading = True
        return cer_str

    def _get_sello(self):
        context = self.env.context.copy()
        certificate_lib = self.env['facturae.certificate.library']
        fname_sign = certificate_lib.b64str_to_tempfile('', file_suffix='.txt', file_prefix='odoo__' + (False or '') + \
            '__sign__')
        result = certificate_lib.with_context(context)._sign(fname=context['fname_xml'],
            fname_xslt=context['fname_xslt'], fname_key=context['fname_key'],
            fname_out=fname_sign, encrypt="sha1", type_key='PEM',context=context)
        return result

    def _xml2cad_orig(self):
        context = self.env.context.copy()
        certificate_lib = self.env['facturae.certificate.library']
        fname_tmp = certificate_lib.b64str_to_tempfile('', file_suffix='.txt', file_prefix='odoo__' + (False or '') + \
            '__cadorig__')
        cad_orig = certificate_lib._transform_xml(fname_xml=context['fname_xml'],
            fname_xslt=context['fname_xslt'], fname_out=fname_tmp)
        return fname_tmp, cad_orig

    def _get_noCertificado(self, fname_cer, pem=True):
        certificate_lib = self.env['facturae.certificate.library']
        fname_serial = certificate_lib.b64str_to_tempfile('', file_suffix='.txt', file_prefix='odoo__' + (False or '') + \
            '__serial__')
        result = certificate_lib._get_param_serial(
            fname_cer, fname_out=fname_serial, type='PEM')
        return result

    def binary2file(self,binary_data, file_prefix="", file_suffix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodebytes(binary_data)) #decodestring=>decodebytes#
        f.close()
        os.close(fileno)
        return fname

    def _get_file_globals(self):
        context = self.env.context.copy()
        file_globals = {}
        if self:
            #payslip = self.browse(cr, uid, id, context=context)
            tz = pytz.timezone('America/Mexico_City')
            time_now=datetime.now(tz).strftime('%H:%M:%S')
            #time_now=datetime.now().strftime('%H:%M:%S')
            # Create a template and pass a context
            date_payment = datetime.strptime(
                    datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S'
                ).strftime('%Y-%m-%d %H:%M:%S')
            ###########################
            #context.update({'date_work':datetime.strptime(
            #    self.payment_id.payment_datetime,'%Y-%m-%d'
            #).strftime('%Y-%m-%d')})

            context.update({'date_work':datetime.strptime(
                datetime.now().strftime('%Y-%m-%d'),'%Y-%m-%d'
            ).strftime('%Y-%m-%d')})

            ###############################
            #file_globals.update({'date_stamped':datetime.strptime(
            #    self.payment_id.payment_datetime,'%Y-%m-%d'
            #).strftime('%Y-%m-%d'),'datetime':date_payment})
            # raise UserError( str( self.payment_id.date.strftime('%Y-%m-%d') ))
            date=datetime.strptime(
                self.payment_id.date.strftime('%Y-%m-%d'),'%Y-%m-%d'
            ).strftime('%Y-%m-%d')

            file_globals.update({'date':date,'datetime':date_payment})

            ########################################
            certificate_id = self.company_id.with_context(context)._get_current_certificate()[self.company_id.id]
            # certificate_id = self.company_id.with_context(
            #     context)._get_current_certificate(
            #     [self.company_id.id])[self.company_id.id]
            #raise UserError(str( certificate_id))

            #certificate_id = certificate_id and self.env['res.company.facturae.certificate'].browse([certificate_id])[0] or False    
            #raise UserError(str( certificate_id  ))
            if certificate_id:
                #raise UserError(str(certificate_id))
                if not certificate_id.certificate_file_pem:
                    pass
                fname_cer_pem = False
                try:
                    fname_cer_pem = self.binary2file(
                        certificate_id.certificate_file_pem, 'odoo_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.cer.pem')
                except:
                    raise UserError(
                        _('Not captured a CERTIFICATE file in format PEM, in '
                           'the company!')
                    )
                file_globals['fname_cer'] = fname_cer_pem

                fname_key_pem = False
                try:
                    fname_key_pem = self.binary2file(
                        certificate_id.certificate_key_file_pem, 'odoo_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.key.pem')
                except:
                    raise UserError(
                        _('Not captured a KEY file in format PEM, in the company!')
                    )
                file_globals['fname_key'] = fname_key_pem

                fname_cer_no_pem = False
                try:
                    fname_cer_no_pem = self.binary2file(
                        certificate_id.certificate_file, 'odoo_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.cer')
                except:
                    pass
                file_globals['fname_cer_no_pem'] = fname_cer_no_pem
                fname_key_no_pem = False
                try:
                    fname_key_no_pem = self.binary2file(
                        certificate_id.certificate_key_file, 'odoo_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.key')
                except:
                    pass
                file_globals['fname_key_no_pem'] = fname_key_no_pem

                file_globals['password'] = certificate_id.certificate_password

                if certificate_id.fname_xslt:
                    if (certificate_id.fname_xslt[0] == os.sep or \
                        certificate_id.fname_xslt[1] == ':'):
                        file_globals['fname_xslt'] = certificate_id.fname_xslt
                    else:
                        file_globals['fname_xslt'] = os.path.join(
                            tools.config["root_path"], certificate_id.fname_xslt)
                else:
                    all_paths = tools.config["addons_path"].split(",")
                    for my_path in all_paths:
                        if os.path.isdir(os.path.join(my_path,
                            'l10n_mx_facturae', 'SAT')):
                            file_globals['fname_xslt'] = my_path and os.path.join(
                                my_path, 'l10n_mx_facturae', 'SAT',
                                'cadenaoriginal_2_0_l.xslt') or ''
                            break
                if not file_globals.get('fname_xslt', False):
                    raise UserError(
                        _('Not defined fname_xslt. !')
                    )

                if not os.path.isfile(file_globals.get('fname_xslt', ' ')):
                    raise UserError(
                        _('No exist file [%s]. !') % (file_globals.get('fname_xslt', ' '))
                    )

                file_globals['serial_number'] = certificate_id.serial_number
            else:
                raise UserError(
                    _('Check date of invoice and the validity of certificate'
                      ', & that the register of the certificate is active.')
                )

        payment_datetime = self.payment_id.payment_datetime.strftime('%Y-%m-%d %H:%M:%S')
        #payslip = self.browse(cr, uid, ids, context=context)
        pac_type=True
        #type_inv = payslip.journal_id.type_cfdi or 'cfd22'
        if payment_datetime < '2012-07-01':
            return file_globals
        elif pac_type:
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_facturae', 'SAT')
                ):
                    file_globals['fname_xslt'] = my_path and os.path.join(
                        my_path, 'l10n_mx_facturae', 'SAT',
                        'cadenaoriginal_4_0',
                        'cadenaoriginal_4_0.xslt') or ''
        return file_globals

    def _get_signed_xml(self,xmldata):

        context = self.env.context.copy()
        fname = (self.company_id.partner_id.vat_split+'_P'+'.xml')
        file_globals=self._get_file_globals()

        #################################
        fname_cer_no_pem = file_globals['fname_cer']
        cerCSD = fname_cer_no_pem and base64.b64encode(open(fname_cer_no_pem, "r").read().encode('utf-8')) or ''
        fname_key_no_pem = file_globals['fname_key']
        keyCSD = fname_key_no_pem and base64.b64encode(open(fname_key_no_pem, "r").read().encode('utf-8')) or ''

        context.update(file_globals)
        comprobante = xmldata.getElementsByTagName("cfdi:Comprobante")[0]
        noCertificado = self._get_noCertificado(context['fname_cer'])
        comprobante.setAttribute("NoCertificado", noCertificado)

        pagos10 = xmldata.getElementsByTagName('pago10:Pago')

        # raise UserError( str( xmldata.toxml('UTF-8') ))
        for attr in pagos10:
            #self.payment_id.currency_id
            # if self.payment_id.journal_id.currency_id and self.payment_id.journal_id.currency_id.id!= self.payment_id.company_id.currency_id.id:
            #     pass
            # else:
            #     attr.removeAttribute('TipoCambioP')
            if not self.payment_id.partner_bank_id or self.payment_id.partner_bank_id.bank_id.bic==False:
                attr.removeAttribute('RfcEmisorCtaOrd')
            elif self.payment_id.journal_id.payment_type_id and self.payment_id.journal_id.payment_type_id.code not in\
            ['03','04']:
                attr.removeAttribute('RfcEmisorCtaOrd')
                #payment_type=self.payment_id.journal_id.payment_type_id.code

        docrelacionado = xmldata.getElementsByTagName('pago10:DoctoRelacionado')
        for attr in docrelacionado:
            se=attr.attributes['Serie'].value
            mfac=attr.attributes['MonedaDR'].value
            mpago=pagos10[0].attributes['MonedaP'].value
            if se=='False':
                attr.removeAttribute('Serie')
            #if factura==compania aand pagos !=compania
            #if mfac=='MXN' and mpago=='USD':
            #    ratedr=self.voucher_id._get_currency_rate_mp()
            #    attr.setAttribute("TipoCambioDR", str(ratedr))
            if not self.payment_id.journal_id.currency_id and mfac!=mpago:
                rate=self.payment_id.get_currency_rate(moneda=mfac)
                attr.setAttribute("TipoCambioDR", str( round(rate,4)))
                #raise UserError( str( rate))

            if mfac==mpago:
                attr.removeAttribute('TipoCambioDR')
        #################################
        pagos_number = "sn"
        (fileno_xml, fname_xml) = tempfile.mkstemp(
        '.xml', 'odoo_' + (pagos_number or '') + '__pagos_v1__')
        fname_txt = fname_xml + '.txt'


        with open(fname_xml,'w') as f:
            f.write(xmldata.toxml("utf-8").decode("utf-8"))
        f.close()
        os.close(fileno_xml)

        (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'odoo_' + (
            pagos_number or '') + '__payment_txt_md5__')
        os.close(fileno_sign)
        context.update({
            'fname_xml': fname_xml,
            'fname_txt': fname_txt,
            'fname_sign': fname_sign,
        })
        fname_txt, txt_str = self.with_context(context)._xml2cad_orig()
        # raise UserError( str( txt_str ))
        context.update({'cadena_original':txt_str})
        if not txt_str:
            raise UserError(
                _("Can't get the string original of the payment.\n"
                  "Ckeck your configuration.")
            )
        sign_str = self.with_context(context)._get_sello()
        ##certificado
        cert_str = self._get_certificate_str(context['fname_cer'])
        cert_str = cert_str.replace(' ', '').replace('\n', '')
        # get_qrcode = self.payment_id.get_qrcode(payment) 

        nodeComprobante = xmldata.getElementsByTagName("cfdi:Comprobante")[0]
        nodeComprobante.setAttribute("Sello", sign_str)
        nodeComprobante.setAttribute("Certificado", cert_str)
        data = {
            'no_certificado': noCertificado,
            'certificado': cert_str,
            'sello': sign_str,
            'cadena_original': txt_str,
            'date_payment_tz':file_globals['datetime']
            # 'qrcode': get_qrcode
        }
        self.payment_id.write(data)

        xmldata = xmldata.toxml('UTF-8')
        return xmldata

    def _get_cfdi_dict_data(self):
        ####### usd!=mxn factura pesos -pago dolares
        #{%  if payment.currency_id.id==item.get('pago').company_currency_id.id and item.get('pago').debit_currency_id.id!=item.get('pago').credit_currency_id.id: %}

        currency_credit=self.payment_ids.filtered(lambda x:x.debit_currency_id!=x.credit_currency_id)
        rate=self.payment_id.get_currency_rate() if not currency_credit else  self.payment_id.get_currency_rate( currency_credit.mapped('debit_currency_id')[0])
        move_lines = []
        totales = {'MontoTotalPagos':self.payment_id.amount if self.payment_id.currency_id==self.payment_id.company_id.currency_id else self.payment_id.amount*round(rate,4),
            'TotalRetencionesIVA':0,'TotalRetencionesISR':0,'TotalRetencionesIEPS':0,
            'TotalTrasladosBaseIVA16':0,'TotalTrasladosImpuestoIVA16':0,'TotalTrasladosBaseIVA8':0,'TotalTrasladosImpuestoIVA8':0,
            'TotalTrasladosBaseIVA0':0,'TotalTrasladosImpuestoIVA0':0,'TotalTrasladosBaseIVAExento':0}
        # Crate an environment of jinja in the templates directory
        taxes_traslado_global = []
        taxes_retenciones_global = []
        for line in self.payment_ids.filtered(lambda x:x.debit_move_id.move_id.move_type=='out_invoice'):
            taxes_traslado_line = []
            taxes_retenidos_line = []
            if line.amount:
                #raise UserError( str(  ))
                for tax in line.debit_move_id.move_id.line_ids.filtered(lambda x:x.tax_line_id):
                    line_tax_value=tax.tax_line_id.with_context(force_price_include=True).compute_all(line.amount if line.debit_currency_id==line.credit_currency_id\
                     and line.debit_currency_id==line.company_currency_id else line.debit_amount_currency, currency=line.debit_currency_id)['taxes']
                    if line_tax_value[0]['amount'] >= 0:
                        #Impuesto por factura
                        taxes_traslado_line.append({
                            'BaseDR':round(line_tax_value[0].get('base'),2),'ImporteDR':line_tax_value[0].get('amount'),
                            'ImpuestoDR':tax.tax_line_id.tax_category_id.code_sat,'TasaOCuotaDR':'{:.6f}'.format(tax.tax_line_id.amount/100),
                            'TipoFactorDR':tax.tax_line_id.tax_category_id.type
                        })
                        #Impuesto global traslados
                        BaseP=round(line_tax_value[0].get('base'),2) 

                        if line.debit_currency_id==line.credit_currency_id and line.debit_currency_id==line.company_currency_id:
                            BaseP=round(line_tax_value[0].get('base'),2)
                        elif line.debit_currency_id!=line.credit_currency_id and line.credit_currency_id==line.company_currency_id:
                            BaseP=round(round(line_tax_value[0].get('base')/(1/round(1/round(rate,4),6)),2)*(1/round(1/round(rate,4),6)),6)

                        # elif line.debit_currency_id==line.credit_currency_id and line.credit_currency_id!=line.company_currency_id:
                        #     BaseP=round(line_tax_value[0].get('base')/round(rate,4),2)
                        ##################### 
                        ImporteP=round(line_tax_value[0].get('amount'),2)
                        if line.debit_currency_id==line.credit_currency_id and line.debit_currency_id==line.company_currency_id:
                            ImporteP=round(line_tax_value[0].get('amount'),2)
                        elif line.debit_currency_id!=line.credit_currency_id and line.credit_currency_id==line.company_currency_id:
                            ImporteP=round(round(line_tax_value[0].get('amount')/(1/round(1/round(rate,4),6)),2)*(1/round(1/round(rate,4),6)),2)
                        # elif line.debit_currency_id==line.credit_currency_id and line.credit_currency_id!=line.company_currency_id:
                        #     ImporteP=round(line_tax_value[0].get('amount')/round(rate,4),2) 
                        #aise UserError( str( BaseP))
                        if not taxes_traslado_global:
                            taxes_traslado_global.append({
                                'tax_id':tax.tax_line_id.id,
                                'BaseP':BaseP,
                                'ImporteP':ImporteP,
                                'ImpuestoP':tax.tax_line_id.tax_category_id.code_sat,'TasaOCuotaP':'{:.6f}'.format(tax.tax_line_id.amount/100),'TipoFactorP':tax.tax_line_id.tax_category_id.type
                                })
                        else:
                            repit=False
                            for gbal in taxes_traslado_global:
                                if tax.tax_line_id.id==gbal['tax_id']:
                                    gbal['BaseP']+=BaseP
                                    gbal['ImporteP']+=ImporteP
                                    repit=True
                            if not repit:
                                taxes_traslado_global.append({
                                'tax_id':tax.tax_line_id.id,'BaseP':BaseP,'ImporteP':ImporteP,
                                'ImpuestoP':tax.tax_line_id.tax_category_id.code_sat,'TasaOCuotaP':'{:.6f}'.format(tax.tax_line_id.amount/100),'TipoFactorP':tax.tax_line_id.tax_category_id.type
                                })
                        #Totales impuestos trasladados

                        totales['TotalTrasladosBaseIVA16'] += round(BaseP,2) if line.debit_currency_id!=line.credit_currency_id and line.debit_currency_id!=line.company_currency_id else round(BaseP*round(rate,4),2)
                        totales['TotalTrasladosImpuestoIVA16'] += ImporteP if line.debit_currency_id!=line.credit_currency_id and line.debit_currency_id!=line.company_currency_id else round(ImporteP*round(rate,4),2)
                    move_lines.append({'pago':line,'serie':line.debit_move_id.move_id.journal_id.code,'folio':line.debit_move_id.move_id.name.replace(line.debit_move_id.move_id.journal_id.code,'').replace('/',''),'taxes_traslado_line':taxes_traslado_line,'taxes_retenidos_line':taxes_retenidos_line})

        env = Environment(loader=FileSystemLoader(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '../templates'
            )
        ))
        emitter = (self.company_id)
        tz = pytz.timezone('America/Mexico_City')
        time_now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        date_voucher = datetime.strptime(time_now,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
        # date_payment = datetime.strptime(self.payment_id.payment_datetime,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
        date_payment = datetime.strptime(time_now,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')

        #date_payment = datetime.strptime(self.payment_id.payment_date,'%Y-%m-%d').strftime('%Y-%m-%dT'+'12:00:00')
        #date_stamped = datetime.strptime(self.payment_id.payment_datetime,'%Y-%m-%d').strftime('%Y-%m-%dT'+str(time_now))
        
        template = env.get_template('payment.xml')

        if not self.payment_id.payment_type_id.name:
            raise UserError("Favor de Revisar que  el metodo de \
                Pago %s este bien configurado"%self.payment_id.journal_id.name)

        #xml_data = template.render(
        #    voucher=self.voucher_id,rate=rate,payment_ids=move_lines,
        #    emitter=emitter,date=date_voucher,date_p=date_payment,pagos=move_lines,amount_pay=amount_pay,rate_dr=rate_dr,regimen=regimen
        #    )

        serie, folio = self.payment_id.get_serie()
        xml_data = template.render(
            payment=self.payment_id, payment_ids=move_lines,
            emitter=emitter, date=date_voucher, date_payment=date_payment, 
            rate=round(rate,4),currency_rate=round(1/round(rate,4),6),serie=serie, folio=folio,taxes_traslado_global=taxes_traslado_global,
            taxes_retenciones_global=taxes_retenciones_global,totales=totales
            )

        new_file = tempfile.NamedTemporaryFile(delete=False)
        with codecs.open(new_file.name, 'w', encoding='utf-8') as f:
            unicode = xml_data
            f.write(unicode)
        xml = parse(new_file.name)

        xmldata = self._get_signed_xml(xml)
        #file_globals=self._get_file_globals()
        return xmldata

    def action_sign_payment(self):
        attach = ''
        index_xml = ''
        msj = ''
        attachment_obj = self.env['ir.attachment']
        payment = self.payment_id
        type = self.type
        # raise UserError( str( type ))
        if type:
            type__fc = self.get_driver_fc_sign()
            # raise UserError( str( type__fc ))

            if type in type__fc.keys():
                fname_payment = self.payment_id.get_filename()+ '.xml'
                xml_data = self._get_cfdi_dict_data()
                #raise UserError(str( xml_data  ))
                fdata = base64.encodebytes(xml_data)
                # raise UserError("",str(type__fc[type]()))
                # raise UserError(_("Valores %s")%(type__fc[type]))
                res = type__fc[type](fdata)
                msj = tools.ustr(res.get('msg', False))
                index_xml = res.get('cfdi_xml', False)
                #xml_file = res.get('cfdi_xml', False).encode('UTF-8')
                xml_file = res.get('cfdi_xml', False).encode('UTF-8')
                data_attach = {
                    'name': fname_payment,
                    #'datas': str(base64.b64encode(xml_file), encoding='utf-8'),#base64.encodestring(xml_file),
                    'datas': base64.encodebytes(xml_file),
                    'store_fname': fname_payment,
                    'description': 'Payment-E XML CFD-I SIGN',
                    'res_model': 'account.payment',
                    'res_id':self.payment_id.id,
                }
                # if self.payment_id.move_line_ids:
                #     self.payment_id.move_line_ids.mapped('move_id').sudo().write({
                #         'cfdi_folio_fiscal': self.payment_id.cfdi_folio_fiscal
                #     })
                    # for line in voucher.move_id.line_id:
                    #     if not line.cfdi_folio_fiscal:
                    #         line.sudo().write({'cfdi_folio_fiscal': self.voucher_id.cfdi_folio_fiscal})
                    # self.write({'uuid': self.voucher_id.cfdi_folio_fiscal})    
                    # attach = attachment_obj.create(data_attach)                       
                attach = attachment_obj.create(data_attach)
            else:
                raise UserError(
                    _("Unknow driver for %s" % attach.type)
                )
        # raise UserError( str( attach ))
        vals={
            'file_xml_sign': attach.id or False,
            'state': 'signed',
            'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'msj': msj
            }
        _logger.info("write==============================: %s " % (vals))
        self.write(vals)
        # self.action_printable()
        self.env.cr.commit()
        return True

    def signal_printable(self):
        """
        If attachment workflow hangs we need to send a signal to continue
        """
        return self.action_printable()

    def action_printable(self):
        # if context is None:
        #     context = {}
        aids = ''
        msj = ''
        index_pdf = ''
        attachment_obj = self.env['ir.attachment']
        payment = self.payment_id#.browse(cr, uid, ids)[0].payment_id
        # payment_obj = self.env['account.payment']
        # (fileno, fname) = tempfile.mkstemp(
        #     '.pdf', 'odoo_' + str(payment.id or '') + '__facturae__'
        # )
        # os.close(fileno)
        # payment_obj.create_report(
        #     cr, uid, [payment.id],
        #     'account.payment.payment.webkit', fname
        # )
        #report_name = "l10n_mx_payment_cfdi.report_payments"
        data = {
             'model': 'ir.attachment.payment.mx',
             'ids': self.payment_id.id,
             'form': {}
        }

        #pdf = self.env['report'].sudo().get_pdf([payment.id], report_name)
        report=self.env.ref('l10n_mx_payment_cfdi.report_payment')
        result, format =report.with_context(self.env.context).render_qweb_pdf(self.payment_id.id, data=data)
        #raise UserError(  str(result)+" /// "+str( format ))
        result= str(base64.b64encode(result),encoding='utf-8')

        aids = attachment_obj.create({
                    'name': payment.get_filename() +'.pdf',
                    'res_model': 'account.payment',
                    'res_id':payment.id,
                    'type': 'binary',
                    'datas':result,
                    'datas_fname': payment.get_filename()+ '.pdf',
                })
        # attachment_ids = attachment_obj.search([
        #    ('res_model', '=', 'account.payment'),
        #    ('res_id', '=', payment.id),
        #    ('datas_fname', '=', payment.company_id.partner_id.vat_split + '_' + self.name + '.pdf')]
        # )
        # for attach in attachment_ids:
        #    aids = attach.id
        #    self.write(
        #        {'name': self.name},
        #    )
        # if aids:
        #   msj = _("Attached Successfully PDF\n")
        # else:

        #    raise UserError(
        #        _('"Warning","Not Attached PDF\n"')
        #    )
        if aids:
            msj = _("Attached Successfully PDF\n")
            self.write(
                {'file_pdf': aids.id,
                 'state': 'printable',
                 'msj': msj,
                 'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                 'file_pdf_index': index_pdf},
            )
        # TODO: Remove the need to commit database if not exception
        self.env.cr.commit()
        return True

    def signal_send_customer(self):
        """
        If attachment workflow hangs we need to send a signal to continue
        """
        return self.action_send_customer()

    def action_send_customer(self):
        self.payment_id.action_send_customer_force()
        self.write({'state': 'done'})
        self.env.cr.commit()
        return True
        # if context is None:
        #     context = {}
        attachments = []
        sent = ''
        sent_to = ''
        # Grab payment
        payment = self.payment_id#.browse(cr, uid, ids)[0].invoice_id

        # Grab attachments
        adjuntos = self.env['ir.attachment'].search(
            [('res_model', '=', 'account.payment'),
             ('res_id', '=', payment.id)]
        )
        for attach in adjuntos:#self.pool.get('ir.attachment').browse(cr, uid, adjuntos):
            attachments.append(attach.id)

        # Send mail
        obj_ir_mail_server = self.env['ir.mail_server']
        mail_server_id = obj_ir_mail_server.search([('name', '=', 'FacturaE')])
        if mail_server_id:
            _logger.debug('Testing SMTP servers')
            for smtp_server in mail_server_id:
                try:
                    obj_ir_mail_server.connect(
                        smtp_server.smtp_host, smtp_server.smtp_port,
                        user=smtp_server.smtp_user,
                        password=smtp_server.smtp_pass,
                        encryption=smtp_server.smtp_encryption,
                        smtp_debug=smtp_server.smtp_debug)
                except Exception as e:
                    raise orm.except_orm(
                        _("Connection test failed!"),
                        _("Configure outgoing mail server named FacturaE: %s")
                        % tools.ustr(e)
                    )

            # Server tested, create mail content
            _logger.debug('Start processing mail template')
            # template_pool = self.pool.get('email.template')
            template_id = self.get_tmpl_email_id()
            if not template_id:
                raise UserError(_("non-existent template"))
            # values = template_pool.generate_email(
            #     cr, uid, template_id, payment.id, context=context
            # )
            values = template_id.generate_email(payment.id)
            if not values['email_from'] or not values['email_to']:
                raise UserError(_('email_from is missing or empty after template rendering, send_mail() cannot proceed'))             
            # assert values['email_from'], 'email_from is missing or empty after template rendering, send_mail() cannot proceed'
            # Get recipients
            recipients = values['partner_ids']
            # Create mail
            mail_mail = self.env['mail.mail']
            msg_id = mail_mail.create(values)
            # Process attachments
            # mail_mail.write(
            #     msg_id,
            #     {'attachment_ids': [(6, 0, attachments)],
            #      'recipient_ids': [(6, 0, recipients)]},
            # )
            msg_id.write(
                {'attachment_ids': [(6, 0, attachments)],
                 'recipient_ids': [(6, 0, recipients)]}
            )            
            # Send mail
            mail_mail.send([msg_id])
            #template_pool.send_mail(cr,uid,template_id,invoice.id,force_send=True,context=context)
            # Check mail
            # if payment.partner_id.email:
            #     sent = _("Sent Successfully\n")
            #     sent_to = payment.partner_id.email
            # else:
            #     raise UserError(
            #         _('Your customer does not have email.'
            #             '\nConfigure the mail of your "Customer"')
            #     )    
        else:
            raise UserError( _('Not Found outgoing mail server name of "FacturaE".'
                '\nConfigure the outgoing mail server named "FacturaE"')
            )
        # self.write({'state': 'done', 'sent': sent, 'sent_to': sent_to})
        self.write({'state': 'done'})
        # TODO: Remove the need to commit database if not exception
        self.env.cr.commit()
        return True

    def signal_cancel_payment(self):
        attachment_obj = self.env['ir.attachment']
        # state = False
        for attach in self:
            # if 'cfdi' in attach.type:
            if attach.type:            
                if attach.state not in ['cancel', 'draft', 'confirmed']:
                    type_fc = self.get_driver_fc_cancel()
                    if attach.type in type_fc.keys():
                        cfdi_cancel = type_fc[attach.type]()
                        # cfdi_cancel = type_fc[attach.type]([attach.id])
                        if cfdi_cancel['status']:
                            # # Regenerate PDF file for include CANCEL legend
                            fname = attach.payment_id.company_id.partner_id.vat_split + '_' + attach.payment_id.move_name
                            # result = self._get_invoice_report(attach.payment_id.id)
                            attach_ids = attachment_obj.search(
                                [('res_model', '=', 'account.payment'),
                                 ('res_id', '=', attach.payment_id.id),
                                 ('name', '=', fname + '.pdf')]
                            )
                            # attachment_obj.write(
                            #     cr, uid, attach_ids,
                            #     {'datas': result}
                            # )
                            # # Set ir_attachment to cancel
                            self.write({'state': 'cancel'})
                            state=True
                            # Set null invoice ir_attachment
                            attach_ids.write(
                                {'res_id': False}
                            )
                            if attach_ids:
                                attach_xml_ids = attachment_obj.search(
                                    [('res_model', '=', 'account.payment'),
                                     ('res_id', '=', attach.payment_id.id),
                                     ('name', '=', fname + '.xml')]
                                )
                                if attach_xml_ids:
                                    attach_xml_ids.write(
                                        {'res_id': False}
                                    )
                        # else: #Comentado por que detiene el proceso de cancelacion
                        #     raise UserError(
                        #         _("Couldn't cancel payment")
                        #     )
                    else:
                        raise UserError(
                            _("Unknow driver for %s" % self.type)
                        )
            else:
                raise UserError(
                    _("The Type Electronic Payment Unknow:" + (self.type or ''))
                )
        return

    def get_tmpl_email_id(self):
        email_ids = self.env['mail.template'].search(
            [('model_id.model', '=', 'account.payment'),('name', '=', 'PaymentE')]
        )
        return email_ids and email_ids[0] or False

    # def _get_invoice_report(self):
    #     """
    #     Helper function to create the PDF report file for payments
    #     """
    #     report_name = "account.payment.payment.webkit"
    #     report_service = 'report.' + report_name
    #     service = netsvc.LocalService(report_service)
    #     (result, format) = service.create(
    #         SUPERUSER_ID, [id],
    #         {'model': 'account.payment'}
    #     )
    #     result = base64.b64encode(result)
    #     return result


# class IrAttachment(models.Model):
#     _inherit = 'ir.attachment'

#     def unlink(self):
#         for line in self:
#             attachments = self.env['ir.attachment.payment.mx'].search(
#                 ['|', '|', ('file_input', 'in', self.ids),
#                  ('file_xml_sign', 'in', self.ids), ('file_pdf', 'in', self.ids)
#                  ]
#             )
#             if attachments and line.res_model=='ir.attachment.payment.mx':
#                 raise UserError(_("'Warning!'\n'You can not remove an attachment of an payment'"))
#         return super(IrAttachment, self).unlink()
