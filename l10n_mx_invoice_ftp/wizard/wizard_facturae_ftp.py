# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, orm


class wizard_facturae_ftp(orm.TransientModel):
    _name = 'wizard.facturae.ftp'

    def invoice_ftp(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ftp_id = False
        data = self.read(cr, uid, ids)[0]
        atta_obj = self.pool.get('ir.attachment')
        atta_obj.file_ftp(cr, uid, data['files'], context=context)
        return {}

    def _get_files(self, cr, uid, context=None):
        if context is None:
            context = {}
        atta_obj = self.pool.get('ir.attachment')
        atta_ids = atta_obj.search(cr, uid, [('res_id', 'in', context[
            'active_ids']), ('res_model', '=', context['active_model'])],
            context=context)
        return atta_ids

    _columns = {
        'files': fields.many2many('ir.attachment', 'ftp_wizard_attachment_rel',
            'wizard_id', 'attachment_id', 'Attachments',
            help='Attachments to upload on FTP Server'),
    }

    _defaults = {
        'files': _get_files,
    }
