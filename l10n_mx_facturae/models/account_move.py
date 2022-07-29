# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
import base64
import hashlib
import tempfile
import os
import codecs

from xml.dom import minidom
from xml.dom.minidom import parse
import xml.dom.minidom
from pytz import timezone
import pytz
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.tools.translate import _
from odoo import tools, netsvc
from odoo import SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

def exec_command_pipe(name, *args):
    """
    @param name :
    """
    # Agregue esta funcion, ya que con la nueva funcion original, de tools no
    # funciona
    prog = tools.find_in_path(name)
    if not prog:
        raise Exception('Couldn\'t find %s' % name)
    if os.name == "nt":
        cmd = '"' + prog + '" ' + ' '.join(args)
    else:
        cmd = prog + ' ' + ' '.join(args)
    return os.popen2(cmd, 'b')

# TODO: Eliminar esta funcionalidad, mejor agregar al path la aplicacion
# que deseamos


def find_in_subpath(name, subpath):
    """
    @param name :
    @param subpath :
    """
    if os.path.isdir(subpath):
        path = [dir for dir in map(lambda x: os.path.join(subpath, x),
                os.listdir(subpath)) if os.path.isdir(dir)]
        for dir in path:
            val = os.path.join(dir, name)
            if os.path.isfile(val) or os.path.islink(val):
                return val
    return None

# TODO: Agregar una libreria para esto


def conv_ascii(text):
    """
    @param text : text that need convert vowels accented & characters to ASCII
    Converts accented vowels, ñ and ç to their ASCII equivalent characters
    """
    old_chars = [
        'á', 'é', 'í', 'ó', 'ú', 'à', 'è', 'ì', 'ò', 'ù', 'ä', 'ë', 'ï', 'ö',
        'ü', 'â', 'ê', 'î', 'ô', 'û', 'Á', 'É', 'Í', 'Ó', 'Ú', 'À', 'È', 'Ì',
        'Ò', 'Ù', 'Ä', 'Ë', 'Ï', 'Ö', 'Ü', 'Â', 'Ê', 'Î', 'Ô', 'Û', 'ñ', 'Ñ',
        'ç', 'Ç', 'ª', 'º', '°', ' ', 'Ã', 'Ø'
    ]
    new_chars = [
        'a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', 'o',
        'u', 'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I',
        'O', 'U', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I', 'O', 'U', 'n', 'N',
        'c', 'C', 'a', 'o', 'o', ' ', 'A', '0'
    ]
    for old, new in zip(old_chars, new_chars):
        try:
            text = text.replace(unicode(old, 'UTF-8'), new)
        except:
            try:
                text = text.replace(old, new)
            except:
                raise UserError(
                    _("Can't recode the string [%s] in the letter [%s]") %
                    (text, old)
                )
    return text
class ResPartner(models.Model):
    _inherit = 'res.partner'
    company_name_cfdi=fields.Char(string="Razon Social CFDI")

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_pdf_cfdi(self):
        return self.env.ref('l10n_mx_facturae.action_report_facturae').report_action(self)

    def get_xml_cfdi(self):
        #('store_fname', '=', self.fname_invoice + '.xml'),
        attachment_obj = self.env['ir.attachment']
        attachment_xml_id = attachment_obj.search([
                ('name', '=', self.fname_invoice + '.xml'),
                ('res_model', '=', 'account.move'),
                ('res_id', '=', self.id),
            ], limit=1)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        download_url = '/web/content/' + str(attachment_xml_id.id) + '?download=true'
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    # descatalogado desde odoo v.11, SE comentan lineas adicionales donde hacer referencia a sequence
    # def _get_invoice_sequence(self, field_names=None, arg=False):
    #     res = {}
    #     for invoice in self:
    #         sequence_id = False
    #         company = invoice.company_id
    #         while True:
    #             if invoice.type == 'out_invoice':
    #                 if 'invoice_out_sequence_id' in company._columns:
    #                     sequence_id = company.invoice_out_sequence_id
    #             elif invoice.type == 'out_refund':
    #                 if 'invoice_out_refund_sequence_id' in company._columns:
    #                     sequence_id = company.invoice_out_refund_sequence_id
    #             company = company.parent_id
    #             if sequence_id or not company:
    #                 break
    #         if not sequence_id:
    #             if (
    #                 'invoice_sequence_id' in invoice.journal_id._columns and
    #                 invoice.journal_id.invoice_sequence_id
    #             ):
    #                 sequence_id = invoice.journal_id.invoice_sequence_id
    #             elif (
    #                 'sequence_id' in invoice.journal_id._columns and
    #                 invoice.journal_id.sequence_id
    #             ):
    #                 sequence_id = invoice.journal_id.sequence_id
    #         sequence_id = sequence_id and sequence_id.id or False
    #         if not sequence_id:
    #             sequence_str = 'account.move.' + invoice.type
    #             test = 'code=%s'
    #             self.execute(
    #                 'SELECT id FROM ir_sequence WHERE ' +
    #                 test + ' AND active=%s LIMIT 1', (sequence_str, True))
    #             res2 = self.dictfetchone()
    #             sequence_id = res2 and res2['id'] or False
    #         res[invoice.id] = sequence_id
    #     return res

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

    def action_make_cfd(self, cr, uid, ids, *args):
        self._attach_invoice(cr, uid, ids)
        return True

    # def ________action_number(self, cr, uid, ids, *args):
    #     cr.execute('SELECT id, type, number, move_id, reference '
    #                'FROM account_invoice '
    #                'WHERE id IN (' + ','.join(map(str, ids)) + ')')
    #     obj_inv = self.browse(cr, uid, ids)[0]
    #     invoice_id__sequence_id = self._get_sequence(cr, uid, ids)  
    #     for (id, invtype, number, move_id, reference) in cr.fetchall():
    #         if not number:
    #             tmp_context = {
    #                 'fiscalyear_id': obj_inv.period_id.fiscalyear_id.id,
    #             }
    #             if invoice_id__sequence_id[id]:
    #                 sid = invoice_id__sequence_id[id]
    #                 number = self.pool.get('ir.sequence').get_id(
    #                     cr, uid, sid, 'id=%s', context=tmp_context)
    #             elif obj_inv.journal_id.invoice_sequence_id:
    #                 sid = obj_inv.journal_id.invoice_sequence_id.id
    #                 number = self.pool.get('ir.sequence').get_id(
    #                     cr, uid, sid, 'id=%s', context=tmp_context)
    #             else:
    #                 number = self.pool.get('ir.sequence').get_id(
    #                     cr, uid, 'account.move.' + invtype,
    #                     'code=%s', context=tmp_context)
    #             if not number:
    #                 raise UserError(
    #                     _('No hay una secuencia de folios bien definida. !')
    #                 )
    #             if invtype in ('in_invoice', 'in_refund'):
    #                 ref = reference
    #             else:
    #                 ref = self._convert_ref(cr, uid, number)
    #             cr.execute('UPDATE account_invoice SET number=%s '
    #                        'WHERE id=%d', (number, id))
    #             cr.execute('UPDATE account_move_line SET ref=%s '
    #                        'WHERE move_id=%d AND (ref is null OR ref = \'\')',
    #                       (ref, move_id))
    #             cr.execute('UPDATE account_analytic_line SET ref=%s '
    #                        'FROM account_move_line '
    #                        'WHERE account_move_line.move_id = %d '
    #                        'AND account_analytic_line.move_id = account_move_line.id',
    #                       (ref, move_id))
    #     return True

    def _get_fname_invoice(self):
        # res = {}
        # sequence_obj = self.env['ir.sequence']
        # invoice_id__sequence_id = self._get_invoice_sequence()
        for invoice in self:
            # sequence_id = invoice_id__sequence_id[invoice.id]
            # sequence = False
            # if sequence_id:
            #     sequence = sequence_obj.browse([sequence_id])[0]
            fname = ""
            fname += invoice.company_id.partner_id.vat or ''
            fname += '_'
            number_work = invoice.name or invoice.move_name
            # try:
            #     self.update({'number_work': number_work or False})
            #     fname += sequence and sequence.prefix or ''
            #     fname += '_'
            # except:
            #     pass
            fname += number_work or ''
            invoice.fname_invoice = fname
            # raise UserError( str( fname ))
        # return res

    # def action_cancel_draft(self):
    #     self.write({
    #         'no_certificado': False,
    #         'certificado': False,
    #         'sello': False,
    #         'cadena_original': False,
    #         'date_invoice_cancel': False,
    #         'cfdi_sello':False,
    #         'cfdi_no_certificado':False,
    #         'cfdi_cadena_original':False,
    #         'cfdi_fecha_timbrado': False,
    #         'cfdi_folio_fiscal': False,
    #         'cfdi_fecha_cancelacion': False
    #     })
    #     return super(AccountMove, self).action_cancel_draft()

    # def action_invoice_draft(self):
    #     self.write({
    #         'no_certificado': False,
    #         'certificado': False,
    #         'sello': False,
    #         'cadena_original': False,
    #         'date_invoice_cancel': False,
    #         'cfdi_sello':False,
    #         'cfdi_no_certificado':False,
    #         'cfdi_cadena_original':False,
    #         'cfdi_fecha_timbrado': False,
    #         'cfdi_folio_fiscal': False,
    #         'cfdi_fecha_cancelacion': False,
    #         'rfcprov':False
    #     })
    #     return super(AccountMove, self).action_invoice_draft()

    def action_cancel(self):
        self.write({
            'date_invoice_cancel': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        return super(AccountMove, self).action_cancel()

    def action_date_assign(self, *args):
        context = {}
        currency_mxn_ids = self.env['res.currency'].search([('name', '=', 'MXN')], limit=1)
        currency_mxn_id = currency_mxn_ids and currency_mxn_ids[0] or False
        if not currency_mxn_id:
            raise UserError(
                _('No hay moneda MXN.')
            )
        for id in self:
            invoice = self
            date_format = invoice.invoice_datetime or False
            context['date'] = date_format
            # rate = self.env['res.currency'].compute(invoice.currency_id.id, currency_mxn_id, 1)
            rate = self.env['res.currency']._compute(invoice.currency_id, currency_mxn_id, 1)
            self.write({'rate': rate})
        return super(AccountMove, self).action_date_assign()

    def _get_cfd_xml_invoice(self, field_name=None, arg=False):
        res = {}
        attachment_obj = self.env['ir.attachment']
        for invoice in self:
            attachment_xml_id = attachment_obj.search([
                ('name', '=', invoice.fname_invoice + '.xml'),
                ('store_fname', '=', invoice.fname_invoice + '.xml'),
                ('res_model', '=', 'account.move'),
                ('res_id', '=', invoice.id),
            ], limit=1)
            res[invoice.id] = attachment_xml_id and attachment_xml_id[0] or False
        return res

    def _get_date_invoice_tz(self):
        tz = pytz.timezone('America/Mexico_City')
        time_now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')#('%H:%M:%S')
        self.date_invoice_tz = time_now #datetime.strptime(self.date_invoice,'%Y-%m-%d').strftime('%Y-%m-%d'+' '+str(time_now))
        # self.date_invoice_tz = pytz.utc.localize(datetime.strptime(self.invoice_datetime, '%Y-%m-%d %H:%M:%S')).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')

    # def _get_rate(self):
    #     res = {}
    #     _logger.warning(
    #         'The rate field is depreciated  you '
    #         'should use instead currency_rate'
    #     )
    #     for rec in self:
    #         res[rec.id] = rec.currency_rate
    #     return res

    # Extract date_invoice from original, but add datetime
    # TODO: Is this field really needed?

    @api.onchange('date', 'currency_id')
    def _onchange_currency(self):
        res=super(AccountMove, self)._onchange_currency()
        rate = self.currency_id._convert(1, self.company_id.currency_id, self.company_id,self.invoice_date or fields.Date.context_today(self))
        self.rate=rate
        return res

    fname_invoice = fields.Char(
            compute='_get_fname_invoice',string='File Name Invoice',
            help='Name used for the XML of electronic invoice'
        )
    # TODO: Is this field really needed?
    no_certificado = fields.Char(
            'No. Certificate', size=64, copy=False,
            help='Number of serie of certificate used for the invoice'
        )
    # TODO: Is this field really needed?
    certificado = fields.Text(
            'Certificate', size=64, copy=False,
            help='Certificate used in the invoice'
        )
    # TODO: Is this field really needed?
    sello = fields.Text('Stamp', size=512, copy=False, help='Digital Stamp')
    # TODO: Duplicated field
    cadena_original = fields.Text(
            'String Original', size=512, copy=False,
            help='Data stream with the information contained in the electronic'
            ' invoice'
        )
    date_invoice_cancel = fields.Datetime(
            'Date Invoice Cancelled',
            readonly=True, copy=False, help='If the invoice is cancelled, save the date'
            ' when was cancel'
        )
    # TODO: Is this field really needed?
    cfd_xml_id = fields.Many2one(
            compute='_get_cfd_xml_invoice', method=True,
            type='many2one', relation='ir.attachment', string='XML',
            help='Attachment that generated this invoice'
        )
    rate = fields.Float(
            string = 'T.C', copy=False,digits=(12, 2),
            help='Rate used in the date of invoice'
        )
    # TODO: Is this field really needed?
    cfdi_sello = fields.Text(
            'CFD-I Stamp', copy=False, help='Sign assigned by the SAT'
        )
    # TODO: Is this field really needed?
    cfdi_no_certificado = fields.Char(
            'CFD-I Certificado', size=32, copy=False,
            help='Serial Number of the Certificate'
        )
    # TODO: Is this field really needed?
    cfdi_cadena_original = fields.Text(
            'CFD-I Original String', copy=False,
            help='Original String used in the electronic invoice'
        )
    cfdi_fecha_timbrado = fields.Datetime(
            'CFD-I Date Stamping', copy=False,
            help='Date when is stamped the electronic invoice'
        )
    # TODO: This field and date_canceled used by same pourpose
    cfdi_fecha_cancelacion = fields.Datetime(
            'CFD-I Cancellation Date', copy=False,
            help='If the invoice is cancel, this field '
            'saved the date when is cancel'
        )
    cfdi_folio_fiscal = fields.Char(
            'CFD-I Fiscal folio', copy=False,
            help='Folio used in the electronic invoice'
        )
    invoice_datetime = fields.Datetime(
            'Date Electronic Invoiced ', states={
                'open': [('readonly', True)], 'close': [('readonly', True)]}, copy=False,
            help="Keep empty to use the current date", default=lambda self: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    date_invoice_tz =  fields.Datetime(
            compute='_get_date_invoice_tz', method=True,
            type='datetime', string='Date Invoiced with TZ', store=True, copy=False,
            help='Date of Invoice with Time Zone'
        )
    # payment_type_id = fields.Many2one('payment.type', 'Payment type',
    #         help='Indicates the way it was paid or will be paid the invoice, where the options could be: check, bank transfer, reservoir in '
    #         'account bank, credit card, cash etc. If not know as will be paid the invoice, leave empty and the XML show “Unidentified”.'
    #     )    
    # use_cfdi_id = fields.Many2one(
    #         'use.cfdi', string='Uso CFDI', readonly=True, 
    #         states={'draft': [('readonly', False)]}
    #     )
    rfcprov = fields.Char(
            string='Rfc Prov', size=64, copy=False, readonly=True
        )
    # paymethod = fields.Selection(
    #         [('PUE','Pago en una sola exhibicion'),('PPD','Pago en parcialidades o diferido')], 
    #         string='Metodo Pago', default="PUE", copy=False, readonly=True, states={'draft': [('readonly', False)]}
    #     )
    # replace_cfdi_sat = fields.Boolean(
    #         string="¿Este CFDI sustituye otro CFDI?", copy=False
    #     )
    # type_relation = fields.Selection(
    #         [('01','01-Nota de crédito de los documentos relacionados'),        
    #         ('02','02-Nota de débito de los documentos relacionados'),
    #         ('03','03-Devolución de mercancía sobre facturas o traslados previos'),
    #         ('04','04-Sustitución de los CFDI previos'),
    #         ('05','05-Traslados de mercancias facturados previamente'),
    #         ('06','06-Factura generada por los traslados previos'),
    #         ('07','07-CFDI por aplicación de anticipo')], 
    #         string='Tipo Relacion', readonly=True, copy=False, states={'draft': [('readonly', False)]}
    #     )
    # relation_ids = fields.Many2many('account.move', 
    #         'account_invoice_relation', 'invoice_relation_id', 'invoice_id', 
    #         string="Factura Relacionada", readonly=True, states={'draft': [('readonly', False)]}
    #     )

    def _get_file(self, inv_ids):
        context = self.env.context.copy()
        id = inv_ids[0]
        invoice = self.browse([id])[0]
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
            '.xml' or ''
        aids = self.env['ir.attachment'].search([(
            'datas_fname', '=', invoice.fname_invoice + '.xml'), (
                'res_model', '=', 'account.move'), ('res_id', '=', id)])
        xml_data = ""
        if aids:
            brow_rec = self.env['ir.attachment'].browse(cr, uid, aids[0])
            if brow_rec.datas:
                xml_data = base64.decodestring(brow_rec.datas)
        else:
            fname, xml_data = self._get_facturae_invoice_xml_data(
                cr, uid, inv_ids, context=context)
            self.env['ir.attachment'].create({
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.move',
                'res_id': invoice.id,
            })
        self.fdata = base64.encodestring(xml_data)
        msg = _("Press in the button  'Upload File'")
        # raise UserError(_("Valores de _get_file %s")%(self.fdata))  
        return {'file': self.fdata, 'fname': fname_invoice,
                'name': fname_invoice, 'msg': msg}

    def add_node(self, node_name=None, attrs=None, parent_node=None,
                 minidom_xml_obj=None, attrs_types=None, order=False):
        """
            @params node_name : Name node to added
            @params attrs : Attributes to add in node
            @params parent_node : Node parent where was add new node children
            @params minidom_xml_obj : File XML where add nodes
            @params attrs_types : Type of attributes added in the node
            @params order : If need add the params in order in the XML, add a
                    list with order to params
        """
        if not order:
            order = attrs
        new_node = minidom_xml_obj.createElement(node_name)
        for key in order:
            if attrs_types[key] == 'attribute':
                new_node.setAttribute(key, attrs[key])
            elif attrs_types[key] == 'textNode':
                key_node = minidom_xml_obj.createElement(key)
                text_node = minidom_xml_obj.createTextNode(attrs[key])

                key_node.appendChild(text_node)
                new_node.appendChild(key_node)
        parent_node.appendChild(new_node)
        return new_node

    def _get_type_sequence(self, context=None):
        type_inv = self.journal_id.type_cfdi or 'cfd22'
        if 'cfdi32' in type_inv:  # Revisa si en tipo es cfdi
            comprobante = 'cfdi:Comprobante'
        if 'cfdi33_facturehoy' in type_inv:
            comprobante = 'cfdi:Comprobante'
        else:
            #comprobante = 'Comprobante'
            comprobante = 'cfdi:Comprobante'     
        return comprobante

    def _get_file_cancel(self, inv_ids):
        inv_ids = inv_ids[0]
        atta_obj = self.env['ir.attachment']
        atta_id = atta_obj.search([('res_id', '=', inv_ids), (
            'name', 'ilike', '%.xml')])
        if atta_id:
            atta_brw = atta_obj.browse(atta_id)[0]
            inv_xml = atta_brw.datas or False
        else:
            inv_xml = False
            raise UserError(
                _('State of Cancellation!\n'
                  "This invoice hasn't stamped, so that not possible cancel.")
            )
        return {'file': inv_xml}

    def binary2file(self, binary_data, file_prefix="", file_suffix=""):
        """
        @param binary_data : Field binary with the information of certificate
                of the company
        @param file_prefix : Name to be used for create the file with the
                information of certificate
        @file_suffix : Sufix to be used for the file that create in this function
        """
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(binary_data))
        f.close()
        os.close(fileno)
        return fname

    def _get_file_globals(self):
        context = dict(self._context or {})
        file_globals = {}
        if self:
            context.update({'date_work': self.date_invoice_tz})
            certificate_id = self.company_id._get_current_certificate()[self.company_id.id]#certificate_id = self.env['res.company.facturae.certificate'].browse(self.company_id.sudo()._get_current_certificate()[self.company_id.id])
            if certificate_id:
                if not certificate_id.certificate_file_pem:
                    # generate certificate_id.certificate_file_pem, a partir
                    # del certificate_id.certificate_file
                    pass
                fname_cer_pem = False
                try:
                    fname_cer_pem = self.binary2file(
                        certificate_id.certificate_file_pem, 'odoo_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.cer.pem')
                except:
                    raise UserError(
                        _('Not captured a CERTIFICATE file in format PEM, in the company!')
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
                    # Search char "," for addons_path, now is multi-path
                    all_paths = tools.config["addons_path"].split(",")
                    for my_path in all_paths:
                        if os.path.isdir(os.path.join(my_path,
                            'l10n_mx_facturae', 'SAT')):
                            # If dir is in path, save it on real_path
                            file_globals['fname_xslt'] = my_path and os.path.join(
                                my_path, 'l10n_mx_facturae', 'SAT','cadenaoriginal_4_0',
                                'cadenaoriginal_4_0.xslt') or ''
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

        invoice_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')#self.invoice_datetime 
        type_inv = self.journal_id.type_cfdi or 'cfd22'
        if invoice_datetime < '2012-07-01 00:00:00':
            return file_globals
        elif 'cfdi' in type_inv:
            # Search char "," for addons_path, now is multi-path
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_facturae', 'SAT')
                ):
                    # If dir is in path, save it on real_path
                    file_globals['fname_xslt'] = my_path and os.path.join(
                        my_path, 'l10n_mx_facturae', 'SAT',
                        'cadenaoriginal_4_0',
                        'cadenaoriginal_4_0.xslt') or ''          
        return file_globals

    def _____________get_facturae_invoice_txt_data(self):
        context = dict(self._context)
        # TODO: Transform date to fmt %d/%m/%Y %H:%M:%S
        certificate_lib = self.pool.get('facturae.certificate.library')
        fname_repmensual_xslt = self._get_file_globals(
            cr, uid, ids, context=context)['fname_repmensual_xslt']
        fname_tmp = certificate_lib.b64str_to_tempfile(base64.encodestring(''),
            file_suffix='.txt', file_prefix='odoo__' + (False or '') + \
            '__repmensual__')
        rep_mensual = ''
        for invoice in self:
            xml_b64 = invoice.cfd_xml_id and invoice.cfd_xml_id.datas or False
            if xml_b64:
                fname_xml = certificate_lib.b64str_to_tempfile(
                    xml_b64 or '', file_suffix='.xml',
                    file_prefix='odoo__' + (False or '') + '__xml__')
                rep_mensual += certificate_lib._transform_xml(
                    fname_xml=fname_xml, fname_xslt=fname_repmensual_xslt,
                    fname_out=fname_tmp)
                rep_mensual += '\r\n'
        return rep_mensual, fname_tmp

    def _dict_iteritems_sort(self, data_dict):  # cr=False, uid=False, ids=[], context={}):
        """
        @param data_dict : Dictionary with data from invoice
        """
        key_order = [
            'Emisor',
            'Receptor',
            'Conceptos',
            'Impuestos',
        ]
        keys = data_dict.keys()
        key_item_sort = []
        for ko in key_order:
            if ko in keys:
                key_item_sort.append([ko, data_dict[ko]])
                # keys.pop(keys.index(ko))
        _logger.info("===================================================: %s " % (keys)) 
        if list(keys)==['xmlns:xsi', 'Version', 'xmlns:cfdi', 'Folio', 'Fecha', 'TipoDeComprobante', 'MetodoPago', 'NoCertificado', 'Sello', 'Certificado', 'SubTotal', 'Total', 'Exportacion', 'Serie', 'cfdi:Impuestos', 'TipoCambio', 'Moneda', 'FormaPago', 'LugarExpedicion', 'cfdi:Emisor', 'cfdi:Receptor', 'cfdi:Conceptos']:
            keys=['xmlns:xsi', 'Version', 'xmlns:cfdi','cfdi:Emisor', 'cfdi:Receptor','Folio', 'Fecha', 'TipoDeComprobante', 'MetodoPago', 'NoCertificado', 'Sello', 'Certificado', 'SubTotal', 'Total', 'Exportacion', 'Serie','cfdi:Conceptos', 'cfdi:Impuestos', 'TipoCambio', 'Moneda', 'FormaPago', 'LugarExpedicion']
        for key_too in keys:       
            key_item_sort.append([key_too, data_dict[key_too]])            
        return key_item_sort

    def dict2xml(self, data_dict, node=False, doc=False):
        """
        @param data_dict : Dictionary of attributes for add in the XML
                    that will be generated
        @param node : Node from XML where will be added data from the dictionary
        @param doc : Document XML generated, where will be working
        """
        parent = False
        if node:
            parent = True

        for element, attribute in self._dict_iteritems_sort(data_dict):
            if not parent:
                doc = minidom.Document()
            if isinstance(attribute, dict):
                if not parent:
                    node = doc.createElement(element)
                    self.dict2xml(attribute, node, doc)
                else:
                    child = doc.createElement(element)
                    self.dict2xml(attribute, child, doc)
                    node.appendChild(child)
            elif isinstance(attribute, list):
                child = doc.createElement(element)
                for attr in attribute:
                    if isinstance(attr, dict):
                        self.dict2xml(attr, child, doc)
                node.appendChild(child)
            else:
                if isinstance(attribute, str) or isinstance(attribute, str):
                    # TODO: Remove conv_ascii function
                    attribute = conv_ascii(attribute)
                else:
                    attribute = str(attribute)  
                node.setAttribute(element, attribute)
        if not parent:
            doc.appendChild(node)
        return doc

    # def _get_facturae_invoice_xml_data(self):
    #     # context = dict(self._context or {})
    #     context = self.env.context.copy()
    #     data_dict = self._get_facturae_invoice_dict_data()[0]
    #     doc_xml = self.dict2xml(
    #         # {'Comprobante': data_dict.get('Comprobante')}
    #         {'cfdi:Comprobante': data_dict.get('cfdi:Comprobante')}
    #     )
    #     invoice_number = "sn"
    #     (fileno_xml, fname_xml) = tempfile.mkstemp(
    #         '.xml', 'odoo_' + (invoice_number or '') + '__facturae__')
    #     fname_txt = fname_xml + '.txt'
    #     f = open(fname_xml, 'w')
    #     doc_xml.writexml(
    #         f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')
    #     f.close()
    #     os.close(fileno_xml)

    #     (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'odoo_' + (
    #         invoice_number or '') + '__facturae_txt_md5__')
    #     os.close(fileno_sign)

    #     context.update({
    #         'fname_xml': fname_xml,
    #         'fname_txt': fname_txt,
    #         'fname_sign': fname_sign,
    #     })
    #     context.update(self._get_file_globals())
    #     fname_txt, txt_str = self._xml2cad_orig()
    #     data_dict['cadena_original'] = txt_str

    #     if not txt_str:
    #         raise UserError(
    #             _('Error en Cadena original!\n'
    #               "Can't get the string original of the voucher.\n"
    #               "Ckeck your configuration.")
    #         )
    #     # TODO: Is this really needed yet?
    #     if not data_dict['Comprobante'].get('folio', ''):
    #         raise UserError(
    #             _('Error in Folio!\n'
    #               "Can't get the folio of the voucher.\n"
    #               "Before generating the XML, click on the button, "
    #               "generate invoice.\nCkeck your configuration")
    #         )

    #     context.update({'fecha': data_dict['Comprobante']['fecha']})
    #     sign_str = self._get_sello()
    #     if not sign_str:
    #         raise UserError(
    #             _('Error in Stamp !\n'
    #               "Can't generate the stamp of the voucher.\n"
    #               "Ckeck your configuration")
    #         )

    #     nodeComprobante = doc_xml.getElementsByTagName("Comprobante")[0]
    #     nodeComprobante.setAttribute("Sello", sign_str)
    #     data_dict['Comprobante']['Sello'] = sign_str

    #     noCertificado = self._get_noCertificado(context['fname_cer'])
    #     if not noCertificado:
    #         raise UserError(
    #             _('Error in No. Certificate !\n'
    #               "Can't get the Certificate Number of the voucher.\n"
    #               "Ckeck your configuration.")
    #         )
    #     nodeComprobante.setAttribute("NoCertificado", noCertificado)
    #     data_dict['Comprobante']['NoCertificado'] = noCertificado

    #     cert_str = self._get_certificate_str(context['fname_cer'])
    #     if not cert_str:
    #         raise UserError(
    #             _('Error in Certificate!\n'
    #               "Can't generate the Certificate of the voucher.\n"
    #               "Ckeck your configuration.")
    #         )
    #     cert_str = cert_str.replace(' ', '').replace('\n', '')
    #     nodeComprobante.setAttribute("Certificado", cert_str)
    #     data_dict['Comprobante']['Certificado'] = cert_str
    #     self.write_cfd_data(data_dict)

    #     if context.get('type_data') == 'dict':
    #         return data_dict
    #     if context.get('type_data') == 'xml_obj':
    #         return doc_xml
    #     data_xml = doc_xml.toxml('UTF-8')
    #     data_xml = codecs.BOM_UTF8 + data_xml
    #     fname_xml = (data_dict['Comprobante']['Emisor']['Rfc'] or '') + '_' + (
    #         data_dict['Comprobante'].get('Serie', '') or '') + '_' + (
    #         data_dict['Comprobante'].get('Folio', '') or '') + '.xml'
    #     data_xml = data_xml.replace('<?xml version="1.0" encoding="UTF-8"?>', '<?xml version="1.0" encoding="UTF-8"?>\n')
    #     facturae_version = '2.2'
    #     self.validate_scheme_facturae_xml([data_xml], facturae_version)
    #     data_dict.get('Comprobante', {})
    #     return fname_xml, data_xml


    def _get_facturae_invoice_xml_data(self):
        context = dict(self._context or {})  
        type_inv = self.journal_id.type_cfdi or 'cfd22'
        if 'cfdi32' in type_inv:# or 'cfdi33_facturehoy' in type_inv:
            comprobante = 'cfdi:Comprobante'
            emisor = 'cfdi:Emisor'
            receptor = 'cfdi:Receptor'
            concepto = 'cfdi:Conceptos'
        else:   
            comprobante = 'cfdi:Comprobante'
            emisor = 'cfdi:Emisor'
            receptor = 'cfdi:Receptor'
            concepto = 'cfdi:Conceptos'

        data_dict = self._get_facturae_invoice_dict_data()[0]
        doc_xml = self.dict2xml(
                {comprobante: data_dict.get(comprobante)}
                # {'comprobante': data_dict.get(comprobante)}
            )
        ########
        cfdi=doc_xml.toxml('UTF-8').decode() .replace('Ubicacionn','Ubicacion').replace('</lines>','').replace('<lines>','')
        doc_xml = xml.dom.minidom.parseString(cfdi)
        ############
        invoice_number = "sn"
        (fileno_xml, fname_xml) = tempfile.mkstemp(
            '.xml', 'odoo_' + (invoice_number or '') + '__facturae__')
        fname_txt = fname_xml + '.txt'
        f = open(fname_xml, 'w')
        doc_xml.writexml(
            f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')
        f.close()
        os.close(fileno_xml)

        (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'odoo_' + (
            invoice_number or '') + '__facturae_txt_md5__')
        os.close(fileno_sign)


        context.update({
            'fname_xml': fname_xml,
            'fname_txt': fname_txt,
            'fname_sign': fname_sign,
        })

        
        context.update(self._get_file_globals())
        fname_txt, txt_str = self.with_context(context)._xml2cad_orig()
        data_dict['cadena_original'] = txt_str
        context.update({
            'cadena_original': txt_str
        })
        if not txt_str:
            raise UserError(
                _("Error in Original String!\n"
                  "Can't get the string original of the one.\n"
                  "Ckeck your configuration.")
            )
        # TODO: Is this validation needed?
        if not data_dict[comprobante].get('Folio', ''):
            raise ValidationError(
                _("Error in Folio!\n"                
                  "Can't get the folio of the voucher.\n"
                  "Before generating the XML, click on the button, "
                  "generate invoice.\nCkeck your configuration.\n")
            )

        context.update({'fecha': data_dict[comprobante]['Fecha']})
        sign_str = self.with_context(context)._get_sello()
        if not sign_str:
            raise ValidationError(
                _("Error in Stamp !\n"                
                  "Can't generate the stamp of the voucher.\n"
                  "Ckeck your configuration.")
            )

        nodeComprobante = doc_xml.getElementsByTagName(comprobante)[0]
        nodeComprobante.setAttribute("Sello", sign_str)
        data_dict[comprobante]['Sello'] = sign_str

        noCertificado = self._get_noCertificado(context['fname_cer'])
        if not noCertificado:
            raise ValidationError(
                _("Error in No. Certificate !\n"                
                  "Can't get the Certificate Number of the voucher.\n"
                  "Ckeck your configuration.")
            )
        nodeComprobante.setAttribute("NoCertificado", noCertificado)
        data_dict[comprobante]['NoCertificado'] = noCertificado

        cert_str = self._get_certificate_str(context['fname_cer'])
        if not cert_str:
            raise ValidationError(
                _("Error in Certificate!\n"                
                  "Can't get the Certificate Number of the voucher.\n"
                  "Ckeck your configuration.")
            )
        cert_str = cert_str.replace(' ', '').replace('\n', '')
        nodeComprobante.setAttribute("Certificado", cert_str)
        data_dict[comprobante]['Certificado'] = cert_str

        x = doc_xml.documentElement
        nodeReceptor = doc_xml.getElementsByTagName(receptor)[0]
        nodeConcepto = doc_xml.getElementsByTagName(concepto)[0]
        x.insertBefore(nodeReceptor, nodeConcepto)
        self.write_cfd_data(data_dict)
        
        if context.get('type_data') == 'dict':
            return data_dict
        if context.get('type_data') == 'xml_obj':
            return doc_xml
        data_xml = doc_xml.toxml('UTF-8')
        data_xml = codecs.BOM_UTF8 + data_xml

        fname_xml = (data_dict[comprobante][emisor]['Rfc'] or '') + '_' + (
            data_dict[comprobante].get('Serie', '') or '') + '_' + (
            data_dict[comprobante].get('Folio', '') or '') + '.xml'
        #data_xml = data_xml.replace(
        #    '<?xml version="1.0" encoding="UTF-8"?>',
        #    '<?xml version="1.0" encoding="UTF-8"?>\n')
        return fname_xml, data_xml

    def validate_scheme_facturae_xml(self, datas_xmls=[], facturae_version=None, facturae_type="cfdv", scheme_type='xsd'):
        # TODO: bzr add to file fname_schema
        if not datas_xmls:
            datas_xmls = []
        certificate_lib = self.pool.get('facturae.certificate.library')
        for data_xml in datas_xmls:
            (fileno_data_xml, fname_data_xml) = tempfile.mkstemp('.xml', 'odoo_' + (False or '') + '__facturae__')
            f = open(fname_data_xml, 'wb')
            f.write(data_xml)
            f.close()
            os.close(fileno_data_xml)
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_facturae', 'SAT')):
                    # If dir is in path, save it on real_path
                    fname_scheme = my_path and os.path.join(my_path, 'l10n_mx_facturae', 'SAT', facturae_type + facturae_version + '.' + scheme_type) or ''
                    # fname_scheme = os.path.join(tools.config["addons_path"], u'l10n_mx_facturae', u'SAT', facturae_type + facturae_version +  '.' + scheme_type )
                    fname_out = certificate_lib.b64str_to_tempfile(base64.encodestring(''), file_suffix='.txt', file_prefix='odoo__' + (False or '') + '__schema_validation_result__')
                    result = certificate_lib.check_xml_scheme(fname_data_xml, fname_scheme, fname_out)
                    if result:  # Valida el xml mediante el archivo xsd
                        raise UserError(
                            _('Error al validar la estructura del xml!\n'
                              'Validación de XML versión %s:\n%s' %
                              (facturae_version, result))
                        )
        return True

    def write_cfd_data(self, cfd_data=None,):
        """
        @param cfd_datas : Dictionary with data that is used in facturae CFDI
        """
        if not cfd_data:
            cfd_data = {}

        comprobante = self._get_type_sequence(context=cfd_data)

        noCertificado = cfd_data.get(comprobante, {}).get('NoCertificado', '')
        certificado = cfd_data.get(comprobante, {}).get('Certificado', '')
        sello = cfd_data.get(comprobante, {}).get('Sello', '')
        cadena_original = cfd_data.get('cadena_original', '')
        data = {
            'no_certificado': noCertificado,
            'certificado': certificado,
            'sello': sello,
            'cadena_original': cadena_original,
        }
        self.write(data)
        return True

    def _get_noCertificado(self, fname_cer, pem=True):
        """
        @param fname_cer : Path more name of file created whit information
                    of certificate with suffix .pem
        @param pem : Boolean that indicate if file is .pem
        """
        certificate_lib = self.env['facturae.certificate.library']
        fname_serial = certificate_lib.b64str_to_tempfile(#base64.encodestring(
            '', file_suffix='.txt', file_prefix='odoo__' + (False or '') + \
            '__serial__')
        result = certificate_lib._get_param_serial(
            fname_cer, fname_out=fname_serial, type='PEM')
        return result

    def _get_sello(self):
        # TODO: Put encrypt date dynamic
        context = self.env.context.copy()
        fecha = context['fecha']
        year = float(time.strftime('%Y', time.strptime(
            fecha, '%Y-%m-%dT%H:%M:%S')))
        if year >= 2011:
            encrypt = "sha1"
        if year <= 2010:
            encrypt = "md5"
        certificate_lib = self.env['facturae.certificate.library']
        fname_sign = certificate_lib.b64str_to_tempfile(#base64.encodestring(
            '', file_suffix='.txt', file_prefix='odoo__' + (False or '') + \
            '__sign__')
        result = certificate_lib._sign(fname=context['fname_xml'],
            fname_xslt=context['fname_xslt'], fname_key=context['fname_key'],
            fname_out=fname_sign, encrypt=encrypt, type_key='PEM',context=context)
        return result

    def _xml2cad_orig(self):
        context = self.env.context.copy() 
        doc = minidom.parse(context['fname_xml'])
        nodeComprobante = doc.getElementsByTagName('cfdi:Comprobante')[0]
        # raise UserError("Context"+str(context))
        noCertificado = self._get_noCertificado(context['fname_cer'])    
        # noCertificado = context.get('serial_number')
        # raise UserError("NoCertificado"+str(noCertificado))      
        if not noCertificado:
            raise UserError(
                _('Error in No. Certificate !\n'
                  "Can't get the Certificate Number of the voucher.\n"
                  "Ckeck your configuration.")
            )
        nodeComprobante.setAttribute("NoCertificado", noCertificado)
        xml_doc=doc.toxml()
        # ##
        (fileno_data_xml, fname_data_xml) = tempfile.mkstemp('.xml', 'odoo_l' + (False or '') + '__facturae__')
        f = open(fname_data_xml, 'wb')
        f.write(xml_doc.encode('utf-8'))
        f.close()
        os.close(fileno_data_xml)
        certificate_lib = self.env['facturae.certificate.library']
        fname_tmp = certificate_lib.b64str_to_tempfile(#base64.encodestring(
            '', file_suffix='.txt', file_prefix='odoo__' + (False or '') + \
            '__cadorig__')
        cad_orig = certificate_lib._transform_xml(fname_xml=fname_data_xml,#fname_xml=context['fname_xml'],#
            fname_xslt=context['fname_xslt'], fname_out=fname_tmp)
        return fname_tmp, cad_orig

# TODO: agregar esta funcionalidad con openssl
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
# TODO: agregar esta funcionalidad con openssl

    def _get_md5_cad_orig(self, cadorig_str, fname_cadorig_digest):
        """
        @param cadorig_str :
        @fname cadorig_digest :
        """
        cadorig_digest = hashlib.md5(cadorig_str).hexdigest()
        open(fname_cadorig_digest, "w").write(cadorig_digest)
        return cadorig_digest, fname_cadorig_digest
    
    def _get_facturae_invoice_dict_data(self):
        context = self.env.context.copy()   
        date_tz = []
        if not self.date_invoice_tz:
            self._get_date_invoice_tz()
            date_tz = self.date_invoice_tz or False
        else:
            self._get_date_invoice_tz()
            date_tz = self.date_invoice_tz or False    
        dp_acount=self.env['decimal.precision'].precision_get('Account')
        invoice_data_parents = []
        notacredito=False
        for invoice in self:
            invoice_data_parent = {}
            # if invoice.type == 'out_invoice':
            if invoice.move_type in ('out_invoice','entry'):
                tipoComprobante = 'I'
            # elif invoice.type == 'out_refund':
            elif invoice.move_type == 'out_refund':
                tipoComprobante = 'E'
                notacredito=True
            else:
                raise UserError(
                    _('Only can issue electronic invoice to customers.!')
                )
            # Inicia seccion: Comprobante
            invoice_data_parent['Comprobante'] = {}
            # default data
            invoice_data_parent['Comprobante'].update({
                'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd",
                'Version': "4.0",
                'xmlns:cfdi':"http://www.sat.gob.mx/cfd/4",
            })
            number_work =invoice.name.replace(invoice.journal_id.code,'').replace('/','') #invoice.number or invoice.internal_number
            invoice_data_parent['Comprobante'].update({
                'Folio': number_work,
                # 'Fecha': date_tz,
                'Fecha': date_tz.strftime("%Y-%m-%dT%H:%M:%S"),#
                # (
                #     invoice.date_invoice_tz and
                #     time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(invoice.date_invoice_tz, '%Y-%m-%d %H:%M:%S'))
                #     or ''
                # ),
                'TipoDeComprobante': tipoComprobante,
                'MetodoPago':invoice.payment_method,
                'NoCertificado': '@',
                'Sello': '@',
                'Certificado': '@',
                'SubTotal': "%.2f" % (invoice.amount_untaxed or 0.0),
                #'Descuento': "0",  # Add field general
                'Total': "%.2f" % (invoice.amount_total or 0.0),
                'Exportacion':'01',
            })
            # TODO: El folio sólo se usa para CBB
            # no es necesario estarlo cargando a cada rato
            serie = invoice.journal_id.code or False#journal_id.sequence_id.prefix or False
            if serie:
                invoice_data_parent['Comprobante'].update({
                    'Serie': serie,
                })
            # Termina seccion: Comprobante
            # Inicia seccion: Emisor
            partner_obj = self.env['res.partner']
            address_invoice = invoice.company_id.address_invoice_parent_company_id or False
            address_invoice_parent = (
                invoice.company_id and
                invoice.company_id.address_invoice_parent_company_id or
                False
            )
            #raise UserError("",str(address_invoice_parent))
            if not address_invoice:
                raise UserError(
                    _("Don't have defined the address issuing!")
                )

            if not address_invoice_parent:
                raise UserError(
                    _("Don't have defined an address of invoicing from the company!")
                )

            if not address_invoice_parent.vat:
                raise UserError(
                    _("Don't have defined RFC for the address of invoice to the company!")
                )

            invoice_data = invoice_data_parent['Comprobante']
            if notacredito:
                if not invoice.relation_ids:
                    raise UserError(
                        _("La Nota de credito no cuenta con alguna Factura relacionada")
                    )
                # if not invoice.relation_ids.cfdi_folio_fiscal:
                #     raise UserError(
                #         _("La Factura Relacionada no cuenta con un folio CFDI")
                #     )
                invoice_data['cfdi:CfdiRelacionados'] = {}
                invoice_data['cfdi:CfdiRelacionados']=[{'TipoRelacion':invoice.type_relation}]
                for inv in invoice.relation_ids:
                    #raise UserError( str(invoice_data['cfdi:CfdiRelacionados'] ))#
                    invoice_data['cfdi:CfdiRelacionados'].append({'cfdi:CfdiRelacionado':{'UUID':inv.cfdi_folio_fiscal}})

            elif invoice.replace_cfdi_sat:
                invoice_data['cfdi:CfdiRelacionados'] = {}
                invoice_data['cfdi:CfdiRelacionados']=[{'TipoRelacion':invoice.type_relation}]
                if invoice.type_relation=='07':
                    for r in invoice.relation_ids:
                        invoice_data['cfdi:CfdiRelacionados'].append({'cfdi:CfdiRelacionado':{'UUID':r.cfdi_folio_fiscal}})
                else:
                    for r in invoice.relation_ids:
                        invoice_data['cfdi:CfdiRelacionados'].append({'cfdi:CfdiRelacionado':{'UUID':r.cfdi_folio_fiscal}})
                # invoice_data['cfdi:CfdiRelacionados'] = {}
                # invoice_data['cfdi:CfdiRelacionados']=[{'TipoRelacion':'04'},
                # {'cfdi:CfdiRelacionado':{'UUID':invoice.relation_id.cfdi_folio_fiscal}}]                    

            invoice_data['Emisor'] = {}
            invoice_data['Emisor'].update({

                'Rfc': address_invoice_parent.vat or '',
                'Nombre': address_invoice_parent.name or '',
                'RegimenFiscal': address_invoice_parent.property_account_position_id.clave,
                # Obtener domicilio dinamicamente
            })
            # Inicia seccion: Receptor
            parent_id = invoice.partner_id.commercial_partner_id.id
            parent_obj = partner_obj.browse(parent_id)
            if not parent_obj.vat:
                raise UserError(
                    _("Don't have defined RFC of the partner[%s].") %
                    parent_obj.name
                )
            if not invoice.usocfdi_id:
                raise UserError(
                    _("Ingrese el tipo de uso  de CFDI por el Receptor")
                )    
            # if parent_obj.vat_split and parent_obj.vat[0:2] != 'MX':
            #     rfc = 'XAXX010101000'
            # else:
            rfc = parent_obj.vat
            address_invoice = partner_obj.browse(invoice.partner_id.id)
            if not parent_obj.company_name_cfdi:
                raise UserError(str("Indique la Razon social del Receptor"))
            invoice_data['Receptor'] = {}
            invoice_data['Receptor'].update({
                'Rfc': rfc,
                'Nombre': (parent_obj.company_name_cfdi.strip() or ''),
                'UsoCFDI':invoice.usocfdi_id.code,
                
            })
            # Inicia seccion: Conceptos
            taxes_inv=[]
            invoice_data['Conceptos'] = []
            for line in invoice.invoice_line_ids:
                price_unit = line.quantity != 0 and round(line.price_subtotal / line.quantity,2) or 0.0
                if not line.code_product_sat:
                    raise UserError(
                        _("Favor de revisar que todas las\
                           lines de la factura cuente con un codigo de producto del SAT")
                    )
                if not line.product_unit_sat:
                    raise UserError(
                        _("Favor de revisar que todas las\
                           lines de la factura cuente con unidad de Medida del SAT")
                    )
                concepto = {
                    'ClaveProdServ':line.code_product_sat.code_sat,
                    'ClaveUnidad':line.product_id.product_unit_sat_alternative.code_sat if line.user_uom_alternative==True else line.product_unit_sat.code_sat,
                    'Cantidad': "%.2f" % (line.quantity or 0.0),
                    'Descripcion': line.name or '',
                    'ValorUnitario': "%.2f" % (price_unit or 0.0),
                    'Importe': "%.2f" % (line.price_subtotal or 0.0),
                    'ObjetoImp':'02',

                    # round(line.price_unit *(1-(line.discount/100)),2) or 0.00),
                    # TODO: Falta agregar discount
                }
                # unidad = line.uom_id and line.uom_id.name or _('Unit(s)')
                if line.user_uom_alternative==True:
                    unidad = line.product_id.uom_alternative_id and line.product_id.uom_alternative_id.name or _('Unit(s)')
                else:
                    unidad = line.product_id.uom_id and line.product_id.uom_id.name or _('Unit(s)')
                #unidad = line.product_id.uom_id and line.product_id.uom_id.name or _('Unit(s)')
                if unidad:
                    concepto.update({'Unidad': unidad})
                product_code = line.product_id and line.product_id.default_code or ''
                if product_code:
                    concepto.update({'NoIdentificacion': product_code})

                impuestos_line={}
                # for tx_id in  line.tax_ids:
                line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
                subtotal = line.quantity * line_discount_price_unit
                force_sign = -1 if self.move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
                taxes_res = line.tax_ids._origin.with_context(force_sign=force_sign).compute_all(line_discount_price_unit,
                    quantity=line.quantity, currency=self.currency_id, product=line.product_id, partner=self.partner_id, is_refund=self.move_type in ('out_refund', 'in_refund'))
                # raise UserError("taxes"+ str( taxes_res["taxes"] ))
                for tx in taxes_res["taxes"]:
                    # raise UserError("taxes"+ str( tx ))
                    tax_id=self.env['account.tax'].browse(tx['id'])
                #     ############################################
                    if not taxes_inv:
                        taxes_inv.append({'tax_id':tax_id,'base':tx["base"],'importe':round(tx["amount"],2)})
                    else:
                        repit=False
                        for txinv in taxes_inv:
                            if tax_id.id==txinv['tax_id'].id:
                                txinv['importe']+=round(tx["amount"],2)
                                txinv['base']+=tx["base"]
                                repit=True
                                break
                        if not repit:
                            taxes_inv.append({'tax_id':tax_id,'base':tx["base"],'importe':round(tx["amount"],2)})
                #     ############################################
                    if tx["amount"] >= 0:
                        if 'cfdi:Traslados' not in impuestos_line:
                            impuestos_line.update({'cfdi:Traslados':[] })
                        impuestos_line['cfdi:Traslados'].append({'cfdi:Traslado':dict({
                            'Base': "%.2f" %(tx["base"]),
                            'Impuesto': "002",
                            'TipoFactor':"Tasa",
                            'TasaOCuota': "%.6f" %(tax_id.amount/100),
                            'Importe': "%.2f"%(tx["amount"])
                        })})  
                #     if tx["amount"] <= 0 and tax_id.tax_category_id.name == 'IVA-RET': #else
                #         #_logger.info("=========ressss====================: %s " % (tx))
                #         if 'cfdi:Retenciones' not in impuestos_line:
                #             impuestos_line.update({
                #                 'cfdi:Retenciones': []
                #             })
                #             #impuestos_line['cfdi:Retenciones']#.update({'cfdi:Retencion':[]})
                #         impuestos_line['cfdi:Retenciones'].append({
                #             'cfdi:Retencion': dict({
                #                 'Base': "%.2f" %(amount_base),
                #                 'Impuesto': tax_id.tax_category_id.code_sat,
                #                 'TipoFactor': tax_id.tax_category_id.type,
                #                 'TasaOCuota': "%.6f" %(-1*tax_id.amount/100),
                #                 'Importe': round(-1*(tx["amount"]),dp_acount)
                #             })
                #         })

                if impuestos_line:
                    concepto.update({'cfdi:Impuestos': impuestos_line})
                invoice_data['Conceptos'].append({'Concepto': concepto})
                pedimento = None
                try:
                    pedimento = line.tracking_id.import_id
                    informacion_aduanera = {
                        'numero': pedimento.name or '',
                        'fecha': pedimento.date or '',
                        'aduana': pedimento.customs,
                    }
                    concepto.update(
                        {'InformacionAduanera': informacion_aduanera}
                    )
                except:
                    pass

            # Termina seccion: Conceptos
            # Inicia seccion: impuestos
            invoice_data['cfdi:Impuestos'] = {}
            invoice_data_impuestos = invoice_data['cfdi:Impuestos']
            invoice_data_impuestos['cfdi:Traslados'] = []
            # invoice_data_impuestos['Retenciones'] = []

            tTraslados = tRetenidos = tLocal = 0
            # Init an empty list for ensure required tax are set
            traslados = []
            for tax_line in taxes_inv:
                amount = abs(tax_line['importe'] or 0.0)
                base = abs(tax_line['base'] or 0.0)
                impuesto = {}
                if tax_line['importe'] >= 0:
                    impuesto.update({
                        'Impuesto':"002",
                        'TipoFactor': "Tasa",
                        'TasaOCuota': "%.6f" %(tax_line['tax_id'].amount/100),
                        'Importe': "%.2f" %(amount),
                        'Base':"%.2f" %(base),
                    })
                    invoice_data_impuestos['cfdi:Traslados'].append({'cfdi:Traslado':impuesto})
                    traslados.append("002")
                    tTraslados += round(amount,2)
            if tTraslados:
                invoice_data['cfdi:Impuestos'].update({'TotalImpuestosTrasladados': "%.2f" % (tTraslados)})
                # if tax_line['importe'] <= 0 and tax_line['tax_id'].tax_category_id.name == 'IVA-RET':
                #     impuesto.update({
                #         'Impuesto': tax_line['tax_id'].tax_category_id.code_sat,
                #         'Importe': "%.2f" %(amount)
                #     })
                #     invoice_data_impuestos['Retenciones'].append({'Retencion':impuesto})
                #     tRetenidos += round(amount,2)
                # if tax_line['importe'] <= 0 and tax_line['tax_id'].tax_category_id.name == 'LOCAL':
                
                #     tLocal += round(amount,2)

            # invoice_data['Impuestos'].update({'tTraslados': "%.2f" % (tTraslados)})
            # if tRetenidos:
            #     invoice_data['Impuestos'].update({'tRetenidos': "%.2f" % (tRetenidos)})
            # Termina seccion: impuestos
            ### Inicia seccion: Complemento
            # if invoice.amount_tax_local:
            #     impuesto_locales = {'cfdi:Complemento': {'implocal:ImpuestosLocales':{}}}
            #     impuesto_locales['cfdi:Complemento'].get('implocal:ImpuestosLocales').update({
            #         'version': '1.0',
            #         "TotaldeTraslados": '0.0',
            #         "TotaldeRetenciones": "%.2f" % (tLocal)
            #     })
            #     impuesto_locales['cfdi:Complemento'].get('implocal:ImpuestosLocales').update({
            #         'implocal:RetencionesLocales': {
            #             'ImpLocRetenido': 'CUOTA SINDICAL',
            #             'TasadeRetencion': '2.0',
            #             'Importe': "%.2f" % (tLocal) 
            #         }
            #     })
            #     invoice_data.update(impuesto_locales)
            ### Termina seccion: Complemento
            invoice_data_parents.append(invoice_data_parent)
            invoice_data_parent['state'] = invoice.state
            invoice_data_parent['invoice_id'] = invoice.id
            invoice_data_parent['type'] = invoice.move_type#invoice.type
            invoice_data_parent['invoice_datetime'] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))# invoice.invoice_datetime
            invoice_data_parent['date_invoice_tz'] = invoice.date_invoice_tz
            invoice_data_parent['currency_id'] = invoice.currency_id.id
            date_ctx = {'date': time.strftime("%Y-%m-%d %H:%M:%S")}
            # date_ctx = {'date': invoice.date_invoice_tz and time.strftime(
            #     '%Y-%m-%d', time.strptime(invoice.date_invoice_tz,
            #     '%Y-%m-%d %H:%M:%S')) or False}
            currency = self.env['res.currency'].browse([invoice.currency_id.id])
            rate = currency.rate != 0 and 1.0 / currency.rate or 0.0
            invoice_data_parent['rate'] = rate

        invoice_datetime = invoice_data_parents[0].get('invoice_datetime',    
            {}) and datetime.strptime(invoice_data_parents[0].get(                
            'invoice_datetime', {}), '%Y-%m-%d %H:%M:%S').strftime(
            '%Y-%m-%d') or False
        if not invoice_datetime:
            # TODO: Is this validation needed?
            raise UserError(
                _("Date Invoice Empty!\n" 
                  "Can't generate a invoice without date, make sure that the "
                  "state of invoice not is draft & the date of invoice is "
                  "not empty")
            )
        zipp = self.company_id.partner_id.zip
        if zipp:# and state and country:
            address =zipp #city + ' ' + state + ', ' + country
        else:
            raise UserError(
                _('Address Incomplete!\n'
                  'Ckeck that the address of company issuing of fiscal '
                  'voucher is complete (City - State - Codigo Postal)')
            )

        if not invoice.company_id.partner_id.property_account_position_id.clave:
            raise UserError(
                _('Missing Fiscal Regime!\n'
                  'The Fiscal Regime of the company issuing of fiscal '
                  'voucher is a data required')
            )

        invoice_data_parents[0]['Comprobante'][
            'xsi:schemaLocation'] = 'http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd'
        invoice_data_parents[0]['Comprobante']['Version'] = '4.0'
        invoice_data_parents[0]['Comprobante'][
            'TipoCambio'] = round(invoice.rate,4) if invoice.rate>1 else 1
        invoice_data_parents[0]['Comprobante'][
            'Moneda'] = invoice.currency_id.name or ''
        #invoice_data_parents[0]['Comprobante'][
        #    'NumCtaPago'] = invoice.partner_bank_id.last_acc_number\
        #        or 'No identificado'
        try:
            p_type = invoice.payment_type_id.code or 'No identificado'
        except:
            p_type = 'No identificado'
        invoice_data_parents[0]['Comprobante']['FormaPago'] = p_type
        # invoice_data_parents[0]['Comprobante']['Emisor']['RegimenFiscal'] = {
        #     'Regimen': invoice.company_id.partner_id.\
        #         regimen_fiscal_id.name or ''}
        invoice_data_parents[0]['Comprobante']['LugarExpedicion'] = address
        return invoice_data_parents

    def _get_time_zone(self):
        """
        TODO: Why is this function needed?
        """
        import pytz
        res_users_obj = self.env['res.users']
        userstz = res_users_obj.browse([0]).partner_id.tz
        a = 0
        if userstz:
            hours = pytz.timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.now()
            loc_dt = hours.localize(datetime(now.year, now.month, now.day,
                                             now.hour, now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            s = str(datetime.now(pytz.timezone(userstz)))
            s = s[-6:-3]
            timezone_present = int(s) * -1
            a = timezone_original + ((
                timezone_present + timezone_original) * -1)
        return a

    def write(self, vals):
        if vals.get('date_invoice'):
            vals.update({'invoice_datetime': False})
            self.assigned_datetime(vals)
        if vals.get('invoice_datetime'):
            if vals.get('type') == 'out_invoice' or vals.get('type') == 'out_refund':
                vals.update({'date_invoice': False})
                self.assigned_datetime(vals)
        return super(AccountMove, self).write(vals)

    # @api.model
    # def create(self, vals):
    #     self.assigned_datetime(vals)
    #     return super(AccountMove, self).create(vals)

    # def assigned_datetime(self, values):
    #     import pytz
    #     res_users_obj = self.env['res.users']
    #     userstz = res_users_obj.browse().partner_id.tz
    #     if userstz:
    #         if not values.get('date_invoice'):
    #             values['date_invoice'] = str(datetime.now(
    #                 pytz.timezone(userstz)).strftime('%Y-%m-%d'))
    #         values['invoice_datetime'] = str(datetime.now(
    #             pytz.timezone(userstz)).strftime('%Y-%m-%d %H:%M:%S'))
    #     else:
    #         if not values.get('date_invoice'):
    #             values['date_invoice'] = str(
    #                 datetime.now().strftime('%Y-%m-%d'))
    #         values['invoice_datetime'] = str(
    #             datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
