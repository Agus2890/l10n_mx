# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import release
from odoo.exceptions import UserError, ValidationError

import os
import time
import base64


class ResCompanyFacturaeCertificate(models.Model):
    _name = 'res.company.facturae.certificate'
    _rec_name = 'serial_number'

    company_id = fields.Many2one('res.company', 'Company', required=True,
            default = lambda self: self.env['res.company']._company_default_get('res.company.facturae.certificate'),
            help='Company where you add this certificate')
    certificate_file = fields.Binary('Certificate File',
            filters='*.cer,*.certificate,*.cert', required=True,
            help='This file .cer is proportionate by the SAT')
    certificate_key_file = fields.Binary('Certificate Key File',
            filters='*.key', required=True, help='This file .key is \
            proportionate by the SAT')
    certificate_password = fields.Char('Certificate Password', size=64,
            invisible=False, required=True, help='This password is \
            proportionate by the SAT')
    certificate_file_pem = fields.Binary('Certificate File PEM',
            filters='*.pem,*.cer,*.certificate,*.cert', help='This file is \
            generated with the file.cer')
    certificate_key_file_pem = fields.Binary('Certificate Key File PEM',
            filters='*.pem,*.key', help='This file is generated with the \
            file.key')
    date_start = fields.Date('Date Start', required=False, default= lambda *a: time.strftime('%Y-%m-%d'), help='Date \
            start the certificate before the SAT')
    date_end = fields.Date('Date End', required=True, help='Date end of \
            validity of the certificate')
    serial_number = fields.Char('Serial Number', size=64, required=True,
            help='Number of serie of the certificate')
    fname_xslt = fields.Char('File XML Parser (.xslt)', size=256,
            required=False, help='Folder in server with XSLT file')
    active = fields.Boolean('Active', default= lambda *a: True, help='Indicate if this certificate \
            is active')

    def get_certificate_info(self):
        cer_der_b64str = self.certificate_file
        key_der_b64str = self.certificate_key_file
        password = self.certificate_password
        data = self.onchange_certificate_info()
        if data['warning']:
            raise ValidationError(_("%s, %s")%
                (data['warning']['title'],
                data['warning']['message'])
            )
        return self.write(data['value'])

    @api.onchange('certificate_password')
    def onchange_certificate_info(self):
        """
        @param cer_der_b64str : File .cer in Base 64
        @param key_der_b64str : File .key in Base 64
        @param password : Password inserted in the certificate configuration
        """
        value = {}
        warning = {}
        certificate_lib = self.env['facturae.certificate.library']
        invoice_obj = self.env['account.move']
        certificate_file_pem = False
        certificate_key_file_pem = False
        # if cer_der_b64str and key_der_b64str and password:
        if self.certificate_file and self.certificate_key_file and self.certificate_password:
            fname_cer_der = certificate_lib.b64str_to_tempfile(
                self.certificate_file, file_suffix='.der.cer',
                file_prefix='odoo__' + (False or '') + '__ssl__',)
            fname_key_der = certificate_lib.b64str_to_tempfile(
                self.certificate_key_file, file_suffix='.der.key',
                file_prefix='odoo__' + (False or '') + '__ssl__',)
            fname_password = certificate_lib.b64str_to_tempfile(
                base64.b64encode(self.certificate_password.encode()), file_suffix='der.txt',
                file_prefix='odoo__' + (False or '') + '__ssl__',)
            fname_tmp = certificate_lib.b64str_to_tempfile(
                '', file_suffix='tmp.txt', file_prefix='odoo__' + (
                False or '') + '__ssl__',)

            cer_pem = certificate_lib._transform_der_to_pem(
                fname_cer_der, fname_tmp, type_der='cer')
            cer_pem_b64 = base64.b64encode(cer_pem.encode())

            key_pem = certificate_lib._transform_der_to_pem(
                fname_key_der, fname_tmp, fname_password, type_der='key')
            key_pem_b64 = base64.b64encode(key_pem.encode())

            date_fmt_return = '%Y-%m-%d'
            serial = False
            try:
                serial = certificate_lib._get_param_serial(
                    fname_cer_der, fname_tmp, type='DER')
                value.update({
                    'serial_number': serial,
                })
            except:
                pass
            date_start = False
            date_end = False
            try:
                dates = certificate_lib._get_param_dates(fname_cer_der,
                    fname_tmp, date_fmt_return=date_fmt_return, type='DER')
                date_start = dates.get('startdate', False)
                date_end = dates.get('enddate', False)
                value.update({
                    'date_start': date_start,
                    'date_end': date_end,
                })
            except:
                pass
            os.unlink(fname_cer_der)
            os.unlink(fname_key_der)
            os.unlink(fname_password)
            os.unlink(fname_tmp)

            if not key_pem_b64 or not cer_pem_b64:
                warning = {
                    'title': _('Warning!'),
                    'message': _('You certificate file, key file or password is incorrect.\nVerify uppercase and lowercase')
                }
                value.update({
                    'certificate_file_pem': False,
                    'certificate_key_file_pem': False,
                })
            else:
                value.update({
                    'certificate_file_pem': cer_pem_b64,
                    'certificate_key_file_pem': key_pem_b64,
                })
            return {'value': value, 'warning': warning}# 1 tab de identation


class ResCompany(models.Model):
    _inherit = 'res.company'

    def ____get_current_certificate(self, field_names=None, arg=False):
        if not field_names:
            field_names = []
        res = {}
        for id in self:
            if "tiny" in release.name:
                res[id] = False
                field_names = [field_names]
            else:
                res[id] = {}.fromkeys(field_names, False)
        certificate_obj = self.env['res.company.facturae.certificate']
        date = self._context.get('date', False) or time.strftime('%Y-%m-%d')
        for company in self:
            certificate_ids = certificate_obj.search([
                ('company_id', '=', company.id),
                ('date_start', '<=', date),
                ('date_end', '>=', date),
                ('active', '=', True),
            ], limit=1)
            certificate_id = certificate_ids and certificate_ids[0] or False
            for f in field_names:
                if f == 'certificate_id':
                    if "tiny" in release.name:
                        res[company.id] = certificate_id
                    else:
                        res[company.id][f] = certificate_id
        return res

    def _get_current_certificate(self, field_names=False, arg=False, context=None):
        if context is None:
            context = {}
        res = {}#.fromkeys(ids, False)
        certificate_obj = self.env['res.company.facturae.certificate']

        date = time.strftime('%Y-%m-%d')

        if 'date_work' in context:
            # Si existe este key, significa, que no viene de un function, si no
            # de una invocacion de factura
            date = context['date_work']
            if not date:
                # Si existe el campo, pero no esta asignado, significa que no fue por un function, y que no se requiere la current_date
                # print "NOTA: Se omitio el valor de date"
                return res
        for company in self:
            current_company = company
            certificate_ids = certificate_obj.search([
                ('company_id', '=', company.id),
                ('date_start', '<=', date),
                ('date_end', '>=', date),
                ('active', '=', True),
            ], limit=1)
            certificate_id = certificate_ids and certificate_ids[0] or False
            res[current_company.id] = certificate_id
        return res

    certificate_ids = fields.One2many('res.company.facturae.certificate',
            'company_id', 'Certificates', help='Certificates configurated in \
            this company')
    #compute='_get_current_certificate', method=True,
    certificate_id = fields.Many2one(
            comodel_name='res.company.facturae.certificate',
            string='Certificate Current', help='Serial Number of the \
            certificate active and inside of dates in this company')
        # 'cif_file': fields.binary('Cedula de Identificacion Fiscal'),
    invoice_out_sequence_id = fields.Many2one('ir.sequence',
            string='Invoice Out Sequence', help="The sequence used for invoice out \
            numbers.")
    invoice_out_refund_sequence_id = fields.Many2one('ir.sequence',
            string='Invoice Out Refund Sequence', help="The sequence used for \
            invoice out refund numbers.")

