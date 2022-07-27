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

import logging
import base64
import xml.dom.minidom
import codecs
import time

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.tools.translate import _
from odoo import tools
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    # from SOAPpy import WSDL
    from suds.client import Client 
except:
    logger.error("Package suds.client missed")


class IrAttachmentFacturaeMx(models.Model):
    _inherit = 'ir.attachment.facturae.mx'

    @api.model
    def _get_type(self):
        types = super(IrAttachmentFacturaeMx, self)._get_type()
        types.extend([('cfdi32_pac_sf', 'CFDI 3.3 Solución Factible')])
        return types

    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(IrAttachmentFacturaeMx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_sf': self._upload_ws_file})
        return factura_mx_type__fc

    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(IrAttachmentFacturaeMx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_sf': self.sf_cancel})
        return factura_mx_type__fc

    type = fields.Selection('_get_type',string='Type', required=True, readonly=True, help='Type of Electronic Invoice')

    def sf_cancel(self):
        msg = ''
        certificate_obj = self.env['res.company.facturae.certificate']
        pac_params_obj = self.env['params.pac']
        invoice_obj = self.env['account.invoice']
        for ir_attachment_facturae_mx_id in self:
            status = False
            invoice = ir_attachment_facturae_mx_id.invoice_id.id
            pac_params_ids = pac_params_obj.search([
                ('method_type', '=', 'pac_sf_cancelar'),
                ('company_id', '=', invoice.company_emitter_id.id),
                ('active', '=', True),
            ], limit=1)
            pac_params_id = pac_params_ids and pac_params_ids[0] or False
            if pac_params_id:
                file_globals = invoice_obj._get_file_globals([invoice.id])
                pac_params_brw = pac_params_obj.browse([pac_params_id])[0]
                user = pac_params_brw.user
                password = pac_params_brw.password
                wsdl_url = pac_params_brw.url_webservice
                namespace = pac_params_brw.namespace
                wsdl_client = False
                wsdl_client = WSDL.SOAPProxy(wsdl_url, namespace)
                fname_cer_no_pem = file_globals['fname_cer']
                cerCSD = fname_cer_no_pem and base64.encodestring(
                    open(fname_cer_no_pem, "r").read()) or ''
                fname_key_no_pem = file_globals['fname_key']
                keyCSD = fname_key_no_pem and base64.encodestring(
                    open(fname_key_no_pem, "r").read()) or ''
                zip = False  # Validar si es un comprimido zip, con la extension del archivo
                contrasenaCSD = file_globals.get('password', '')
                uuids = invoice.cfdi_folio_fiscal  # cfdi_folio_fiscal
                params = [
                    user, password, uuids, cerCSD, keyCSD, contrasenaCSD
                ]
                wsdl_client.soapproxy.config.dumpSOAPOut = 0
                wsdl_client.soapproxy.config.dumpSOAPIn = 0
                wsdl_client.soapproxy.config.debug = 0
                wsdl_client.soapproxy.config.dict_encoding = 'UTF-8'
                result = wsdl_client.cancelar(*params)
                codigo_cancel = result['status'] or ''
                status_cancel = result['resultados'] and result[
                    'resultados']['status'] or ''
                mensaje_cancel = _(tools.ustr(result['mensaje']))
                msg_nvo = result['resultados'] and result[
                    'resultados']['mensaje'] or ''
                status_uuid = result['resultados'] and result[
                    'resultados']['statusUUID'] or ''
                folio_cancel = result['resultados'] and result[
                    'resultados']['uuid'] or ''
                if (
                    codigo_cancel == '200' and status_cancel == '200' and
                    (status_uuid == '201' or status_uuid == '202')
                ):
                    msg += mensaje_cancel + _('\n- The process of cancellation\
                    has completed correctly.\n- The uuid cancelled is:\
                    ') + folio_cancel
                    invoice_obj.write(
                        cr, uid, [invoice.id],
                        {'cfdi_fecha_cancelacion': time.strftime('%Y-%m-%d %H:%M:%S')}
                    )
                    status = True
                else:
                    raise UserError(
                        _('Cancel Code: %s.-Status code %s.-Status UUID: %s.-'
                          'Folio Cancel: %s.-Cancel Message: %s.'
                          '-Answer Message: %s.') %
                        (codigo_cancel, status_cancel, status_uuid,
                         folio_cancel, mensaje_cancel, msg_nvo)
                    )
            else:
                msg = _('Not found information of webservices of PAC, verify that the configuration of PAC is correct')
        return {'message': msg, 'status_uuid': status_uuid, 'status': status}

    def _upload_ws_file(self, fdata=None):
        """
        @params fdata : File.xml codification in base64
        """
        context = self._context.copy()
        invoice_obj = self.env['account.invoice']
        pac_params_obj = invoice_obj.env['params.pac'] 
        for ir_attachment_facturae_mx_id in self:
            invoice = ir_attachment_facturae_mx_id.invoice_id
            comprobante = invoice_obj._get_type_sequence()
            cfd_data = base64.b64decode(fdata).decode("utf-8", "ignore") # base64.decodestring(fdata) # or invoice_obj.fdata).replace("<lines>","").replace("</lines>","") 
            # raise UserError(_("Valores cfd_data %s")%(cfd_data))
            xml_res_str = xml.dom.minidom.parseString(cfd_data)
            xml_res_addenda = invoice_obj.add_addenta_xml(xml_res_str, comprobante)
            xml_res_str_addenda = xml_res_addenda.toxml('UTF-8')
            # xml_res_str_addenda = xml_res_str_addenda.replace(codecs.BOM_UTF8, '') 
            if tools.config['test_report_directory']:  # TODO: Add if test-enabled:
                ir_attach_facturae_mx_file_input = ir_attachment_facturae_mx_id.file_input and ir_attachment_facturae_mx_id.file_input or False
                fname_suffix = ir_attach_facturae_mx_file_input and ir_attach_facturae_mx_file_input.datas_fname or ''
                open(os.path.join(tools.config['test_report_directory'], 'l10n_mx_facturae_pac_sf' + '_' + \
                  'before_upload' + '-' + fname_suffix), 'wb+').write(xml_res_str_addenda)
            compr = xml_res_addenda.getElementsByTagName(comprobante)[0]
            date = compr.getAttribute('Fecha')#compr.attributes['Fecha'].value
            date_format = datetime.strptime(
                date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')#'%Y-%m-%dT%H:%M:%S.%fz').strftime('%Y-%m-%d')
            context.update({'date': date_format})# context['date'] = date_format
            invoice_ids = [invoice.id]
            file = False
            msg = ''
            cfdi_xml = False
            pac_params_ids = pac_params_obj.search([
                ('method_type', '=', 'pac_sf_firmar'), (
                    'company_id', '=', invoice.company_id.id), (
                        'active', '=', True)], limit=1)#'The company_emitter_id field is depreciated  you should use instead company_id'
            if pac_params_ids:
                pac_params = pac_params_ids
                user = pac_params.user
                password = pac_params.password
                wsdl_url = pac_params.url_webservice
                namespace = pac_params.namespace
                url = 'https://testing.solucionfactible.com/ws/services/Timbrado?wsdl'
                testing_url = 'http://testing.solucionfactible.com/ws/services/Timbrado'
                if (wsdl_url == url) or (wsdl_url == testing_url):
                    pass
                else:
                    raise UserError(
                        _('Web Service URL o PAC incorrect')
                    )
                if namespace == 'http://timbrado.ws.cfdi.solucionfactible.com':
                    pass
                else:
                    raise UserError(
                        _('Namespace of PAC incorrect')
                    )
                if 'testing' in wsdl_url:
                    msg += _(u'WARNING, SIGNED IN TEST!!!!\n\n')
                # wsdl_client = WSDL.SOAPProxy(wsdl_url, namespace)
                wsdl_client = Client(wsdl_url)
                if True:  # if wsdl_client:
                    file_globals = invoice._get_file_globals()
                    fname_cer_no_pem = file_globals['fname_cer']
                    # cerCSD = fname_cer_no_pem and base64.encodestring(
                    #     open(fname_cer_no_pem, "r").read()) or ''
                    cerCSD = fname_cer_no_pem and bytes(
                        open(fname_cer_no_pem,"r").read().encode('utf-8')) or ''
                    fname_key_no_pem = file_globals['fname_key']
                    # keyCSD = fname_key_no_pem and base64.encodestring(
                    #     open(fname_key_no_pem, "r").read()) or ''
                    keyCSD = fname_key_no_pem and base64.b64encode(
                        open(fname_key_no_pem,"r").read().encode('utf-8')) or ''                    
                    cfdi = str(base64.b64encode(xml_res_str_addenda), encoding='utf-8') #base64.encodestring(xml_res_str_addenda) # #cfd_data not add
                    zip = False  # Validar si es un comprimido zip, con la extension del archivo
                    contrasenaCSD = file_globals.get('password', '')
                    params = [
                        user, password, cfdi, zip]
                    # wsdl_client.soapproxy.config.dumpSOAPOut = 0
                    # wsdl_client.soapproxy.config.dumpSOAPIn = 0
                    # wsdl_client.soapproxy.config.debug = 0
                    # wsdl_client.soapproxy.config.dict_encoding = 'UTF-8'
                    # try:
                    wsdl_client = Client(wsdl_url)
                    resultado = wsdl_client.service.timbrar(user, password, cfdi, zip)
                    # except Exception as e:
                    #     raise ValidationError(str(e))
                    # resultado = wsdl_client.timbrar(*params)
                    htz = int(invoice._get_time_zone())
                    mensaje = _(tools.ustr(resultado['mensaje']))
                    resultados_mensaje = resultado['resultados'] and \
                        resultado['resultados'][0]['mensaje'] or ''
                    folio_fiscal = resultado['resultados'] and \
                        resultado['resultados'][0]['uuid'] or ''
                    codigo_timbrado = resultado['status'] or ''
                    codigo_validacion = resultado['resultados'] and resultado['resultados'][0]['status'] or ''
                    

                    if codigo_timbrado == 311 or codigo_validacion == 311:
                        raise UserError(
                            _('Unauthorized.\nCode 311')
                        )
                    elif codigo_timbrado == 312 or codigo_validacion == 312:
                        raise UserError(
                            _('Failed to consult the SAT.\nCode 312')
                        )
                    elif codigo_timbrado == 200 and codigo_validacion == 200 or codigo_validacion == 307:
                        fecha_timbrado = resultado[
                            'resultados'][0]['fechaTimbrado'] or False
                        # fecha_timbrado = fecha_timbrado and time.strftime(
                        #     '%Y-%m-%d %H:%M:%S', time.strptime(
                        #         fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                        # fecha_timbrado = fecha_timbrado and datetime.strptime(
                        #     fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(
                        #         hours=htz) or False
                        cfdi_data = {
                            'cfdi_cbb': resultado['resultados'][0]['qrCode'] or False,  # ya lo regresa en base64
                            'cfdi_sello': resultado['resultados'][0]['selloSAT'] or False,
                            'cfdi_no_certificado': resultado['resultados'][0]['certificadoSAT'] or False,
                            'cfdi_cadena_original': resultado['resultados'][0]['cadenaOriginal'] or False,
                            'cfdi_fecha_timbrado': fecha_timbrado,
                            'cfdi_xml': str(base64.b64decode(resultado['resultados'][0]['cfdiTimbrado'] or ''),encoding='utf-8'),  # este se necesita en uno que no es base64
                            'cfdi_folio_fiscal': resultado['resultados'][0]['uuid'] or '',
                        }
                        msg += mensaje + "." + resultados_mensaje + \
                            " Folio Fiscal: " + folio_fiscal + "."
                        msg += _(
                                u"\nMake Sure to the file really has generated correctly to the SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html")
                        if cfdi_data.get('cfdi_xml', False):
                            url_pac = '</"%s"><!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://solucionfactible.com/cfdi/00001000000102699425.zip-->' % (
                                comprobante)
                            # cfdi_data['cfdi_xml'] = cfdi_data['cfdi_xml'].replace('</"%s">' % (comprobante), url_pac)
                            # file = base64.encodestring(cfdi_data['cfdi_xml'] or '')
                            parsedata = xml.dom.minidom.parseString( cfdi_data['cfdi_xml'] )
                            complemento = parsedata.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
                            rfcprov = complemento.attributes['RfcProvCertif'].value
                            cfdi_data.update({'rfcprov':rfcprov})
                            # invoice_obj.cfdi_data_write(cr, uid, [invoice.id],
                            # cfdi_data, context=context)
                            cfdi_xml = cfdi_data['cfdi_xml']#.pop('cfdi_xml')
                        if cfdi_xml:
                            invoice.write(cfdi_data)
                            cfdi_data['cfdi_xml'] = cfdi_xml
                        else:
                            msg += _(u"Can't extract the file XML of PAC")
                    else:
                        raise UserError(
                            _('Stamped Code: %s.-Validation code %s.-'
                              'Folio Fiscal: %s.-Stamped Message: %s.-'
                              'Validation Message: %s.') %
                            (codigo_timbrado, codigo_validacion,
                             folio_fiscal, mensaje, resultados_mensaje)
                        )
            else:
                msg += 'Not found information from web services of PAC, verify that the configuration of PAC is correct'
                raise UserError(
                    _('Not found information from web services of PAC,'
                      ' verify that the configuration of PAC is correct')
                )
            return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml}








