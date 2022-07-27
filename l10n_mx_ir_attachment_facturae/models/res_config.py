# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class l10n_mx_email_config_settings(models.TransientModel):
    _name = 'l10n.mx.email.config.settings'
    _inherit = 'res.config.settings'
    _order = "id desc"
    _rec_name = 'email_tmp_id'

    email_tmp_id = fields.Many2one('mail.template', 'Email Template')

    def get_default_email_tmp_id(self, fields):
        email_tmp_id = False
        self.env.cr.execute(
            """ select max(id) as email_tmp_id from l10n_mx_email_config_settings """)
        dat = self.env.cr.dictfetchall()
        data = dat and dat[0]['email_tmp_id'] or False
        if data:
            email_tmp_id = self.browse(data).email_tmp_id
        else:
            try:
                email_tmp_id = self.env['ir.model.data'].get_object('l10n_mx_ir_attachment_facturae',
                    'email_template_template_facturae_mx')
            except:
                pass
        return {'email_tmp_id': email_tmp_id and email_tmp_id.id or False}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
