# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def cfdi_data_write(self,cfdi_data):
        """
        @params cfdi_data : * TODO
        """
#         ids = isinstance(ids, (int, long)) and [ids] or ids
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

    def add_addenta_xml(self,xml_res_str=None, comprobante=None):
        """
         @params xml_res_str : File XML
         @params comprobante : Name to the Node that contain the information the XML
        """
        if xml_res_str:
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
