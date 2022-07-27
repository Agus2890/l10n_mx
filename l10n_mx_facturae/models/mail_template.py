# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class MailTemplate(models.Model):
    """ Extend generic message composition wizard to auto attach invoice
        related files when sending opening the Send Mail invoice button.
    """
    _inherit = 'mail.template'

    def generate_email(self, res_ids, fields=None):
        res = super(MailTemplate, self).generate_email(res_ids, fields=fields)
        if isinstance(res, dict) and type(res_ids) is int:#is not int:
            if res['model'] == 'account.move': #if res[res_ids[0]]['model']=='account.move':
                states = ['printable', 'sent_customer', 'done']
                att_obj = self.env['ir.attachment.facturae.mx']
                iatt_ids = att_obj.search([('invoice_id', '=', res_ids)])#res_ids[0])])

                #raise Warning( str(iatt_ids ))
                for iattach in iatt_ids:
                    attachments = []
                    if iattach.state in states:
                        attachments.append(iattach.file_xml_sign.id)
                        attachments.append(iattach.file_pdf.id)
                        res['attachment_ids'] = attachments#res[res_ids[0]]['attachment_ids'] = attachments
        return res


    def generate_email_batch(self, template_id, res_ids):
        """
        Generates an email from the template for given (model, res_id) pair.

       :param template_id: id of the template to render.
       :param res_id: id of the record to use for rendering the template (model
                      is taken from template definition)
       :returns: a dict containing all relevant fields for creating a new
                 mail.mail entry, with one extra key ``attachments``, in the
                 fmodelsat expected by :py:meth:`mail_thread.message_post`.
        """
        att_obj = self.env['ir.attachment.facturae.mx']
        ir_model_data = self.env['ir.model.data']
        
        reference_ids = []
        states = ['printable', 'sent_customer', 'done']
        data = {
            'account': 'email_template_edi_invoice',
            'portal_sale': 'email_template_edi_invoice',
            'l10n_mx_ir_attachment_facturae': 'email_template_template_facturae_mx',
        }
        values = super(EmailTemplate, self).generate_email_batch(template_id, res_ids)
        
        # Look for possible templates for invoice and override
        for module, name in data.iteritems():
            try:
                reference_ids.append(ir_model_data.get_object_reference(module, name)[1])
            except ValueError:
                # Template not installed so we catch the error
                # and skip error messages
                continue
            
        if template_id in reference_ids:
            for res_id in res_ids:
                iatt_ids = att_obj.search(
                    cr, uid,
                    [('invoice_id', '=', res_id)],
                    context=context
                )
                for iattach in att_obj.browse(cr, uid, iatt_ids, context=context):
                        attachments = []
                        if iattach.state in states:
                            # Attach XML file to mesage
                            attachments.append(iattach.file_xml_sign.id)
                            # Attach PDF file to mesage
                            attachments.append(iattach.file_pdf.id)
                            values[res_id]['attachment_ids'] = attachments
        return values
