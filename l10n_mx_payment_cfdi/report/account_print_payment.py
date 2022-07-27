# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import string
import base64
#import cStringIO
from io import StringIO,BytesIO
import time
from odoo import models, fields, _, api
from odoo.exceptions import UserError
import qrcode


class Report_invoice_Cfdi(models.AbstractModel):
    _name = 'report.l10n_mx_payment_cfdi.report_payments'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.payment',
            'docs': docs,
            'data':data,
            'get_payment_lines':self.get_payment_lines(docs),
            #'amount_text':docs.get_amount_text(),
            #'qrcode':self.get_qrcode(docs),
            #'get_taxes':self.get_taxes(docs),
            #'get_taxes_ret':self._get_taxes_ret(docs),
        }

    @api.model
    def get_payment_lines(self, payment):
        return payment.get_payment_invoice() 

