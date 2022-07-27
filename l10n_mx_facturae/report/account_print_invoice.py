# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import string
import logging
import base64
from io import StringIO,BytesIO
import time

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import qrcode
import logging
logger = logging.getLogger(__name__)


class ReportInvoiceCfdi(models.AbstractModel):
    _name = 'report.l10n_mx_facturae.report_invoice_cfdi'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': docs,
            'data': data,
            # 'amount_text': docs._get_amount_to_text(),
            'qrcode': self.get_qrcode(docs),
            'get_text_promissory': self.get_text_promissory(docs),
        }

    def get_text_promissory(self,invoice):
        text = ''
        # for inv in invoice: 
        #     company = inv.company_id
        #     if company.dinamic_text:
        #             text = company.dinamic_text % eval("{" + company.dict_var + "}")
        return text

    @api.model
    def get_qrcode(self, invoice):
        """Genera el código de barras bidimensional para una factura
            @param invoice: Objeto invoice con los datos de la factura

            @return: Imagen del código de barras o None
        """
        output_s=False
        for inv in invoice: 
            # Procesar invoice para obtener el total con 17 posiciones
            tt = str.zfill('%.6f' % inv.amount_total, 17)
            ## Procesar invoice para obtener los ocho últimos caracteres del sello digital del emisor del comprobante.
            fe = inv.sello[-8:]
            # Init qr code
            qr = qrcode.QRCode(version=4, box_size=4, border=1)
            qr.add_data('https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=' + inv.company_id.partner_id.vat_split or inv.company_id.partner_id.vat)        
            qr.add_data('&id=' + inv.cfdi_folio_fiscal)              
            qr.add_data('&rr=' + inv.partner_id.vat_split or inv.company_id.vat)
            qr.add_data('&tt=' + tt)
            qr.add_data('&fe=' + fe)
            qr.make(fit=True)
            img = qr.make_image()
            output = BytesIO()
            img.save(output,'PNG')
            output_s = output.getvalue()
        return base64.b64encode(output_s)

    @api.model
    def _get_taxes(self, invoice):
        lista = []
        lista2 = []

        taxes = []
        for line in invoice.invoice_line_ids:
            for tax in line.invoice_line_tax_ids:
                taxes.append(tax)
        for tax in taxes:
            lista.append([tax.name, tax.amount])

        for i in range(0, len(lista)):
            for j in range(i + 1, len(lista)):
                if (lista[i][0] == lista[j][0]) and (lista[j][0] != 0):
                    lista[j][0] = 0
                    lista[i][1] = lista[i][1] + lista[j][1]

        for k in range(0, len(lista)):
            if lista[k][0] != 0:
                lista2.append(lista[k])

        lst2 = [item[0][0:8] for item in lista2]
        return lst2

    @api.model
    def _get_taxes_ret(self, invoice):
        lista = []
        lista2 = []
        taxes = [tax for tax in invoice.tax_line_ids if tax.tax_id.amount < 0.0]
        for tax in taxes:
            lista.append([tax.name2, tax.amount])

        for i in range(0, len(lista)):
            for j in range(i + 1, len(lista)):
                if (lista[i][0] == lista[j][0]) and (lista[j][0] != 0):
                    lista[j][0] = 0
                    lista[i][1] = lista[i][1] + lista[j][1]

        for k in range(0, len(lista)):
            if lista[k][0] != 0:
                lista2.append(lista[k])
        return lista2

