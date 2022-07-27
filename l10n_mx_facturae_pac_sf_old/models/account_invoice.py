# -*- encoding: utf-8 -*-
##############################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2008 MKI - http://www.mikrointeracciones.com.mx
#    All Rights Reserved.
#    info@mikrointeracciones.com.mx
##############################################################################
#    Coded by: Ricardo Gutiérrez (ricardo.gutierrez@mikrointeracciones.com.mx)
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # cfdi_cbb = fields.Binary('CFD-I CBB')
    # cfdi_sello = fields.Text('CFD-I Sello', help='Sign assigned by the SAT')
    # cfdi_no_certificado = fields.Char('CFD-I Certificado', size=32,
    #                                        help='Serial Number of the Certificate')
    # cfdi_cadena_original = fields.Text('CFD-I Cadena Original',
    #                                         help='Original String used in the electronic invoice')
    # cfdi_fecha_timbrado = fields.Datetime('CFD-I Fecha Timbrado',
    #                                            help='Date when is stamped the electronic invoice')
    # cfdi_fecha_cancelacion = fields.Datetime('CFD-I Fecha Cancelacion',
    #                                               help='If the invoice is cancel, this field saved the date when is cancel')
    # cfdi_folio_fiscal = fields.Char('CFD-I Folio Fiscal', size=64,
    #                                      help='Folio used in the electronic invoice')

    def cfdi_data_write(self, cfdi_data):
        """
        @params cfdi_data : * TODO
        """
        # ids = isinstance(ids, (int, long)) and [ids] or ids
        attachment_obj = self.env['ir.attachment']
        cfdi_xml = cfdi_data.pop('cfdi_xml')
        if cfdi_xml:
            self.write(cfdi_data)
            cfdi_data[
                'cfdi_xml'] = cfdi_xml  # Regresando valor, despues de hacer el write normal
            """for invoice in self.browse(cr, uid, ids):
                #fname, xml_data = self.pool.get('account.invoice').\
                    _get_facturae_invoice_xml_data(cr, uid, [inv.id],
                    context=context)
                fname_invoice = invoice.fname_invoice and invoice.\
                    fname_invoice + '.xml' or ''
                data_attach = {
                    'name': fname_invoice,
                    'datas': base64.encodestring( cfdi_xml or '') or False,
                    'datas_fname': fname_invoice,
                    'description': 'Factura-E XML CFD-I',
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }
                attachment_ids = attachment_obj.search(cr, uid, [('name','=',\
                    fname_invoice),('res_model','=','account.invoice'),(
                    'res_id', '=', invoice.id)])
                if attachment_ids:
                    attachment_obj.write(cr, uid, attachment_ids, data_attach,
                        context=context)
                else:
                    attachment_obj.create(cr, uid, data_attach, context=context)
                """
        return True

    def add_addenta_xml(self, xml_res_str=None, comprobante=None):
        """
         @params xml_res_str : File XML
         @params comprobante : Name to the Node that contain the information the XML
        """
        if not xml_res_str:# se agrega not para envitar crear el nodo addenda
            node_Addenda = xml_res_str.getElementsByTagName('cfdi:Addenda')
            if len(node_Addenda) == 0:
                nodeComprobante = xml_res_str.getElementsByTagName(
                    comprobante)[0]
                node_Addenda = self.add_node(
                    'cfdi:Addenda', {}, nodeComprobante, xml_res_str, attrs_types={})
                node_Partner_attrs = {
                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id': "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf': 'attribute',
                    'xsi:schemaLocation': 'attribute',
                    'id': 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
            else:
                node_Partner_attrs = {
                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id': "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf': 'attribute',
                    'xsi:schemaLocation': 'attribute',
                    'id': 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
        return xml_res_str
