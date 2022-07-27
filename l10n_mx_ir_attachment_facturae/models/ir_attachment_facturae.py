# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import tools
from odoo import netsvc
import time
import tempfile
import base64
import os
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, RedirectWarning

import logging
_logger = logging.getLogger(__name__)


class IrAttachmentFacturaeMx(models.Model):
    _name = 'ir.attachment.facturae.mx'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def _get_type(self):
        types = []
        return types

    def get_driver_fc_sign(self):
        """function to inherit from custom PAC module"""
        return {}

    def get_driver_fc_cancel(self):
        """function to inherit from custom PAC module"""
        return {}

    name = fields.Char(
            'Name', size=128, required=True, readonly=True,
            help='Name of attachment generated'
        )
    uuid = fields.Char(
            'UUID', size=128, readonly=True,
            help='UUID of attachment stamped'
        )    
    move_id = fields.Many2one(
            'account.move', 'Invoice', readonly=True,
            help='Invoice to which it belongs this attachment'
        )
    company_id = fields.Many2one(
            'res.company', 'Company', readonly=True,
            help='Company to which it belongs this attachment',
            default=lambda self: self.env['res.company']._company_default_get('ir.attachment.facturae.mx')
        )
    file_input = fields.Many2one(
            'ir.attachment', 'File input',
            readonly=True, help='File input'
        )
    file_input_index = fields.Text(
            'File input', help='File input index'
        )
    file_xml_sign = fields.Many2one(
            'ir.attachment', 'File XML Sign',
            readonly=True, help='File XML signed'
        )
    file_xml_sign_index = fields.Text(
            'File XML Sign Index',
            help='File XML sign index'
        )
    file_pdf = fields.Many2one(
            'ir.attachment', 'File PDF', readonly=True,
            help='Report PDF generated for the electronic Invoice'
        )
    file_pdf_index = fields.Text(
            'File PDF Index', help='Report PDF with index'
        )
    identifier = fields.Char(
            'Identifier', size=128,
        )
    type = fields.Selection(
            [], 'Type', help="Type of Electronic Invoice"
        )
    description = fields.Text('Description')
    msj = fields.Text(
            'Last Message', readonly=True,
            track_visibility='onchange',
            help='Message generated to upload XML to sign'
        )
    last_date = fields.Datetime(
            'Last Modified', readonly=True,
            help='Date when is generated the attachment', default =lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
        )
    sent = fields.Text(
            'Sent', readonly=True, 
            help='Confirmed shipping message'
        )
    sent_to = fields.Text(
            'Sent to', readonly=True, 
            help='Customer mail'
        )
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('signed', 'Signed'),
            ('printable', 'Printable Format Generated'),
            ('sent_customer', 'Sent Customer'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'), ],
            'State', readonly=True, required=True, help='State of attachments', default='draft'
        )

    def action_confirm(self):
        invoice_obj = self.env['account.move']
        msj = ''
        index_xml = ''
        attach = self.browse()
        invoice = attach.move_id
        type = attach.type
        save_attach = None
        if 'cfdi' in type:
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                '_V3_3.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data([invoice.id])
            attach = self.env['ir.attachment'].create({
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.move',
                'res_id': invoice.id,
            })
            msj = _("Attached Successfully XML CFDI 3.3\n")
            save_attach = True
        else:
            raise UserError(
                _("Type Electronic Invoice Unknow!\n"
                  "The Type Electronic Invoice:" + (type or ''))
            )
        if save_attach:
            self.write({
                'file_input': attach or False,
                'state': 'confirmed',
                'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'msj': msj,
                'file_xml_sign_index': index_xml},
            )
        return True

    def action_sign(self):       
        attach = ''
        index_xml = ''
        msj = ''
        invoice = self.move_id
        attachment_obj = self.env['ir.attachment']
        type = self.type
        # raise UserError(str(type))
        if type:
            # Get all drivers available for sign an attachment file
            type__fc = self.get_driver_fc_sign()
            if type in type__fc.keys():
                # fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                #     '.xml' or ''
                fname_invoice = self.name+'.xml' or ''    
                fname, xml_data = invoice._get_facturae_invoice_xml_data()
                _logger.info('XML before signed: --------------------> %s' % (xml_data))
                fdata = base64.encodebytes(xml_data) 
                res = type__fc[type](fdata)
                msj = tools.ustr(res.get('msg', False))
                index_xml = res.get('cfdi_xml', False)
                xml_file = res.get('cfdi_xml', False).encode('UTF-8')  
                data_attach = {
                    'name': fname_invoice,
                    'datas': base64.encodebytes(xml_file),
                    'store_fname': fname_invoice,
                    'description': 'Factura-E XML CFD-I SIGN',
                    'res_model': 'account.move',
                    'res_id': invoice.id,
                }
                # Write cfdi in models
                invoice.write({'cfdi_folio_fiscal': invoice.cfdi_folio_fiscal})
                # for line in invoice.move_id.line_ids:
                #     if not line.cfdi_folio_fiscal:
                #         line.sudo().write({'cfdi_folio_fiscal': invoice.cfdi_folio_fiscal})
                # self.write({'uuid': invoice.cfdi_folio_fiscal})        
                # Context, because use a variable type of our code but we
                # dont need it.
                attach = attachment_obj.create(data_attach)
                # raise UserError(_(Valores %s)%(attach.type))
            else:
                raise UserError(
                    _("Unknow driver for %s")%(type)
                )
        self.write({
            'file_xml_sign': attach.id or False,
            'state': 'signed',
            'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'msj': msj,
            'file_xml_sign_index': index_xml,
            },
        )
        # TODO: Remove the need to commit database if not exception
        self.action_printable()
        #self.action_send_customer(cr, uid, ids, context=context)
        self.env.cr.commit()
        return True

    def signal_printable(self):
        """
        If attachment workflow hangs we need to send a signal to continue
        """
        return self.action_printable()

    def action_printable(self):
        aids = ''
        msj = ''
        index_pdf = ''
        # attachment_obj = self.env['ir.attachment']
        # invoice = self.move_id#.browse(cr, uid, ids)[0].move_id        
        # invoice_obj = self.env['account.move']

        # (fileno, fname) = tempfile.mkstemp(
        #     '.pdf', 'openerp_' + (invoice.fname_invoice or '') + '__facturae__'
        # )
        # raise Warning(_("Valores %s")%(fname))
        # os.close(fileno)
        # invoice_obj.create_report(
        #     [invoice.id],
        #     "account.move.facturae.webkit", fname
        # )

        data = {
             'model': 'account.move',
             'ids': self.move_id.id,
             'form': {}
        }

        report = self.env.ref('l10n_mx_facturae.action_report_facturae')
        result, format = report.with_context(self.env.context)._render_qweb_pdf(self.move_id.id, data=data)
        result = str(base64.b64encode(result),encoding='utf-8')
        aids = self.env['ir.attachment'].create({
                'name': self.move_id.fname_invoice+str('.pdf'),
                'datas': result,
                'store_fname': self.move_id.fname_invoice+str('.pdf') ,
                # 'description': 'Factura-E PDF',
                'res_model': 'account.move',
                'res_id': self.move_id.id,
            })

        # attachment_ids = attachment_obj.search([
        #     ('res_model', '=', 'account.move'),
        #     ('res_id', '=', invoice.id),
        #     ('datas_fname', '=', invoice.fname_invoice + '.pdf')]
        # )
        # for attach in attachment_ids:
        #     # TODO: WHY????
        #     # aids.append( attachment.id ) but without error in last write
        #     aids = attach.id
        #     self.write(
        #         {'name': invoice.fname_invoice + '.pdf', }
        #     )
        if aids:
            msj = _("Attached Successfully PDF\n")
        else:
            raise UserError(
                _('Not Attached PDF\n')
            )
        self.write({
            'file_pdf': aids.id or False,
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
        attachments = []
        sent = ''
        sent_to = ''        
        # Grab invoice
        move = self.move_id

        # Grab attachments
        adjuntos = self.env['ir.attachment'].search(
            [('res_model', '=', 'account.move'),
             ('res_id', '=', move.id)]
        )
        for attach in adjuntos:
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
                    raise UserError(
                        _("Connection test failed!\n"
                          "Configure outgoing mail server named FacturaE: %s")
                          % tools.ustr(e)
                    )

            # Server tested, create mail content
            _logger.debug('Start processing mail template')
            # template_pool = self.env['email.template']
            template_id = self.get_tmpl_email_id()
            values = template_id.generate_email(move.id)
            assert values.get('email_from'), 'email_from is missing or empty after template rendering, send_mail() cannot proceed'
            # Get recipients
            recipients = values['partner_ids']
            # Create mail
            mail_mail = self.env['mail.mail']
            msg_id = mail_mail.create(values)
            # Process attachments
            msg_id.write({
                'attachment_ids': [(6, 0, attachments)],
                'recipient_ids': [(6, 0, recipients)]},
            )
            # Send mail
            mail_mail.send([msg_id])
            # Check mail
            if move.partner_id.email:
                sent = _("Sent Successfully\n")
                sent_to = move.partner_id.email
            else:
                raise UserError(
                    _('Your customer does not have email.'
                        '\nConfigure the mail of your "Customer"')
                )             
        else:
            raise UserError(
                _('Not Found outgoing mail server name of "FacturaE".'
                  '\nConfigure the outgoing mail server named "FacturaE"')
            )
        self.write({'state': 'done', 'sent': sent, 'sent_to': sent_to})
        # TODO: Remove the need to commit database if not exception
        self.env.cr.commit()
        return True

    def signal_cancel(self):
        attachment_obj = self.env['ir.attachment']
        for attach in self:
            if 'cfdi' in attach.type:
                if attach.state not in ['cancel', 'draft', 'confirmed']:
                    type_fc = self.get_driver_fc_cancel()
                    if attach.type in type_fc.keys():
                        cfdi_cancel = type_fc[attach.type]([attach.id])
                        if cfdi_cancel['status']:
                            # Regenerate PDF file for include CANCEL legend
                            fname = attach.move_id.fname_invoice
                            result = self._get_invoice_report(attach.move_id.id)
                            attach_ids = attachment_obj.search(
                                [('res_model', '=', 'account.move'),
                                 ('res_id', '=', attach.move_id.id),
                                 ('name', '=', fname + '.pdf')]
                            )
                            attachment_obj.write(attach_ids,
                                {'datas': result}
                            )
                            # Set ir_attachment to cancel
                            self.write(attach.id, {'state': 'cancel'})
                        else:
                            raise UserError(
                                _("Couldn't cancel invoice")
                            )
                    else:
                        raise UserError(
                            _("Unknow driver for %s" % attach.type)
                        )
                else:
                    self.write({'state': 'cancel'})         
            else:
                raise UserError(
                    _("Type Electronic Invoice Unknow!\n"
                      "The Type Electronic Invoice:" + (attach.type or ''))
                )
        return

    def reset_to_draft(self, *args):
        self.write({'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for row in self.ids:
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, self._name, row)
            wf_service.trg_create(uid, self._name, row)
        return True

    def get_tmpl_email_id(self):
        email_ids = self.env['mail.template'].search(
            [('model_id.model', '=', 'account.move')]
        )
        return email_ids and email_ids[0] or False

    def _get_invoice_report(self, cr, uid, id, context=None):
        """
        Helper function to create the PDF report file for invoices
        """
        report_name = "account.move.facturae.webkit"
        report_service = 'report.' + report_name
        service = netsvc.LocalService(report_service)
        (result, format) = service.create(
            cr, SUPERUSER_ID, [id],
            {'model': 'account.move'}, context=context
        )
        result = base64.b64encode(result)
        return result


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self):
        attachments = self.env['ir.attachment.facturae.mx'].search(
            ['|', '|', ('file_input', 'in', self.ids),
             ('file_xml_sign', 'in', self.ids), ('file_pdf', 'in', self.ids)
             ]
        )
        if attachments:
            raise UserError(
                _('You can not remove an attachment of an invoice')
            )
        return super(IrAttachment, self).unlink()
