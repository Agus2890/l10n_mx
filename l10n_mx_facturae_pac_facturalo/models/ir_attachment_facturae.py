# -*- encoding: utf-8 -*-
##############################################################################
#    Module Writen to Odoo, Open Source Management Solution
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
from suds.client import Client # from SOAPpy import WSDL
from requests import Request, Session, exceptions

class IrAttachmentFacturaeMx(models.Model):
    _inherit = 'ir.attachment.facturae.mx'

    @api.model
    def _get_type(self):
        types = super(IrAttachmentFacturaeMx, self)._get_type()
        types.extend([('cfdi_pac_xpd','CFDI 4.0 Expide tu factura')])
        return types

    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(IrAttachmentFacturaeMx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi_pac_xpd': self._upload_ws_file_xpd})
        return factura_mx_type__fc

    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(IrAttachmentFacturaeMx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi_pac_xpd': self.sf_cancel})
        return factura_mx_type__fc

    type = fields.Selection('_get_type',string='Type', required=True, readonly=True, help='Type of Electronic Invoice')

    def sf_cancel(self):
        msg = ''
        certificate_obj = self.env['res.company.facturae.certificate']
        pac_params_obj = self.env['params.pac']
        invoice_obj = self.env['account.move']
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

    def _upload_ws_file_xpd(self, fdata=None):
        context = self._context.copy()
        invoice_obj = self.env['account.move']
        pac_params_obj = invoice_obj.env['params.pac']
        for ir_attachment_facturae_mx_id in self:
            file = False
            msg = ''
            cfdi_xml = False
            invoice = ir_attachment_facturae_mx_id.move_id#invoice_id
            cfd_data = base64.b64decode(fdata or invoice_obj.fdata).decode("utf-8", "ignore")
            xml_res_str = xml.dom.minidom.parseString(cfd_data)

            xml_res_str_addenda = xml_res_str.toxml('UTF-8')#.decode("utf-8", "ignore")
            #raise UserError( str( xml_res_str_addenda.decode("utf-8", "ignore")  ))
            #compr = xml_res_str.getElementsByTagName(comprobante)[0]
            # date = compr.getAttribute('Fecha')
            # date_format = datetime.strptime(
            #     date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
            # context.update({'date': date_format})
            #invoice_ids = [invoice.id]
            file = False
            msg = ''
            cfdi_xml = False
            pac_params_ids = pac_params_obj.search([
                ('method_type', '=', 'pac_xpd_firmar'), (
                    'company_id', '=', invoice.company_id.id),
                    ('active', '=', True)], limit=1)
            
            if pac_params_ids:
                pac_params =pac_params_ids 
                user = pac_params.user
                password = pac_params.password
                wsdl_url = pac_params.url_webservice
                namespace = pac_params.namespace
                
                wsdl_client = Client(wsdl_url)
                #zip = False 
                cfdi = str(base64.b64encode(xml_res_str_addenda), encoding='utf-8')
                # raise UserError( str( wsdl_client))
                #cfdi = str(base64.b64encode(cfd_data), encoding='utf-8')

                #cfdi = base64.b64encode(xml_res_str_addenda)
                #raise UserError( str( cfdi ))
                #resultado = wsdl_client.service.timbrar(user, password, fdata.decode() , zip)
                #raise UserError( str(timbrar ))
                try:
                    resultado =  wsdl_client.service.timbrar(user,password,cfdi)
                except Exception as e:
                    raise ValidationError('Server timeout.'+str(e))

                mensaje = resultado['mensaje']
                #valid_codes = ['200']
                # resultados_mensaje = resultado['resultados'] and \
                #     resultado['resultados'][0]['mensaje'] or ''
                # folio_fiscal = resultado['resultados'] and \
                #     resultado['resultados'][0]['uuid'] or ''
                # codigo_timbrado = resultado['status'] or ''
                codigo_validacion = resultado['codigo']# and resultado['resultados'][0]['status'] or ''
                #raise ValidationError( str(resultado ))
                if resultado['codigo'] in ['200']:
                    timbre = resultado['timbre'].encode('UTF-8')
                    parsedata = xml.dom.minidom.parseString(timbre)
                    complemento = parsedata.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
                    logger.info("regex====================: %s " % (timbre))
                    ###########
                    # Obtiene el sello del SAT
                    try:
                        selloSAT =complemento.attributes['SelloSAT'].value 
                        #re.search('SelloSAT="(.+?)" ', timbref).group(1)
                    except:
                        selloSAT = ''
                    # Obtiene el nuúmero de certificado
                    try:
                        no_certificado = complemento.attributes['NoCertificadoSAT'].value
                        #re.search('NoCertificadoSAT="(.+?)" ', timbref).group(1)
                    except:
                        no_certificado = ''
                    # Obtiene la fecha en que se timbó la factura
                    try:
                        fecha = complemento.attributes['FechaTimbrado'].value
                        #re.search('FechaTimbrado="(.+?)" ', timbref).group(1)
                    except:
                        fecha = ''

                    # Obtiene el folio de la factura
                    try:
                        uuid = complemento.attributes['UUID'].value
                        #re.search('UUID="(.+?)" ', timbref).group(1)
                    except:
                        uuid = ''
                    # Obtiene el RFC provedor servicio
                    try:
                        rfcprov = complemento.attributes['RfcProvCertif'].value
                        #re.search('RfcProvCertif="(.+?)" ', timbref).group(1)
                    except:
                        rfcprov = ''

                    # Obtiene la cadena original
                    #raise UserError( str( invoice.sello))
                    try:
                        version = complemento.attributes['Version'].value
                        cadena = ('|').join([version,
                                             uuid,
                                             str(invoice.date_invoice_tz),
                                             invoice.sello,
                                             str(no_certificado)])
                        cadena = "||{0}||".format(cadena)
                    except:
                       cadena = ''
                    ############
                    # fecha_timbrado = resultado[
                    #     'resultados'][0]['fechaTimbrado'] or False
                    # fecha_timbrado = fecha_timbrado and time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(
                    #     str(fecha_timbrado)[:19], '%Y-%m-%d %H:%M:%S')) or False
                    cfdi_data = {
                        'cfdi_sello': selloSAT,
                        'cfdi_no_certificado': no_certificado,
                        'cfdi_cadena_original': cadena,
                        'cfdi_fecha_timbrado': str(fecha).replace('T',' '),
                        'cfdi_folio_fiscal': uuid,
                        'rfcprov':rfcprov,
                        #'cfdi_xml':timbre,#str(base64.b64decode(resultado['resultados'][0]['cfdiTimbrado'] or ''),encoding='utf-8'),  # este se necesita en uno que no es base64
                    }
                    # cfdi_data = {
                    #     'cfdi_sello': resultado['resultados'][0]['selloSAT'] or False,
                    #     'cfdi_no_certificado': resultado['resultados'][0]['certificadoSAT'] or False,
                    #     'cfdi_cadena_original': resultado['resultados'][0]['cadenaOriginal'] or False,
                    #     'cfdi_fecha_timbrado': fecha_timbrado,
                    #     #'cfdi_xml': str(base64.b64decode(resultado['resultados'][0]['cfdiTimbrado'] or ''),encoding='utf-8'),  # este se necesita en uno que no es base64
                    #     'cfdi_folio_fiscal': resultado['resultados'][0]['uuid'] or '',
                    # }
                    invoice.write(cfdi_data)
                    msg=mensaje
                    cfdi_xml =timbre.decode("utf-8", "ignore")#str(base64.b64decode(timbre),encoding='utf-8') #cfdi_data['cfdi_xml']#.pop('cfdi_xml')
                    
                else:
                    msg = "Codigo de Error:" + str(codigo_validacion) + str(mensaje)
                    raise UserError(_("%s")%(msg))

            else:
                raise UserError(_('Warning!\nNot found information from web services of PAC,\n  verify that the configuration of PAC is correct'))
            return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml}








