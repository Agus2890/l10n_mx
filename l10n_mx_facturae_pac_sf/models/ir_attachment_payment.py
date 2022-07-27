# -*- encoding: utf-8 -*-
##############################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2008 MKI - 
#    All Rights Reserved.
##############################################################################
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

import re
import logging
import string
import base64
# import xmltodict
from odoo.exceptions import UserError, ValidationError, RedirectWarning
# from SOAPpy import WSDL
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import tools
import codecs
import xml.dom.minidom
from requests import Request, Session, exceptions
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta

try:
    # from SOAPpy import WSDL
    from suds.client import Client
except:
    logger.error("Package suds.client missed")


TIMEOUT = 60


class IrAttachmentPaymentMx(models.Model):
    _inherit = 'ir.attachment.payment.mx'

    @api.model
    def _get_type(self):
        types=super(IrAttachmentPaymentMx,self)._get_type()
        types.extend([('cfdi32_pac_sf', 'CFDI 3.3 Solución Factible')])
        return types

    type=fields.Selection('_get_type',string='Type')

    def get_driver_fc_sign(self):
        drivers = super(IrAttachmentPaymentMx, self).get_driver_fc_sign()
        drivers.update({'cfdi32_pac_sf': self.sign_file_sf})
        return drivers

    def get_driver_fc_cancel(self):
        drivers = super(IrAttachmentPaymentMx, self).get_driver_fc_cancel()
        drivers.update({'cfdi32_pac_sf': self.cancel_file_sf})
        return drivers

    def cancel_file_sf(self):
        # if context is None:
        #     context = {}
        msg = ''
        certificate_obj = self.env['res.company.facturae.certificate']
        pac_params_obj = self.env['params.pac']
        payment_obj = self.env['account.payment']
        for ir_attachment_facturae_mx_id in self:#.browse(cr, uid, ids, context=context):
            status = False
            payment = ir_attachment_facturae_mx_id.payment_id
            pac_params_ids = pac_params_obj.search([
                ('method_type', '=', 'pac_sf_cancelar'),
                ('company_id', '=', payment.company_id.id),
                ('active', '=', True),
            ], limit=1)
            if not pac_params_ids:
                raise UserError(
                    _('Not found information from web services of PAC'
                      'Verify that the configuration of PAC is correct')
                )
            pac_params_id = pac_params_ids and pac_params_ids[0] or False
            if pac_params_id:
                file_globals = self._get_file_globals()
                pac_params_brw = pac_params_id#pac_params_obj.browse([pac_params_id])[0]
                user = pac_params_brw.user
                password = pac_params_brw.password
                wsdl_url = pac_params_brw.url_webservice
                namespace = pac_params_brw.namespace ## revisar si funcional namespace = 'http://ws.cfdi.solucionfactible.com'
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
                uuids = payment.cfdi_folio_fiscal  # cfdi_folio_fiscal
                # rfc_emisor = payment.company_id.partner_id.vat_split
                # params = [user, password, rfc_emisor, uuids, cerCSD, keyCSD, contrasenaCSD]
                params = [user, password, uuids, cerCSD, keyCSD, contrasenaCSD]
                wsdl_client.soapproxy.config.dumpSOAPOut = 0
                wsdl_client.soapproxy.config.dumpSOAPIn = 0
                wsdl_client.soapproxy.config.debug = 0
                wsdl_client.soapproxy.config.dict_encoding = 'UTF-8'
                result = wsdl_client.cancelar(*params)
                codigo_cancel = result['status'] or ''
                raise UserError("status_cancel",str(result))
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
                    # invoice_obj.write([invoice.id],
                    #     {'cfdi_fecha_cancelacion': time.strftime('%Y-%m-%d %H:%M:%S')}
                    # )
                    self.payment_id.write({'cfdi_fecha_cancelacion': time.strftime('%Y-%m-%d %H:%M:%S')})
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
        # raise UserError("status_cancel",str(status_uuid))        
        return {'message': msg, 'status_uuid': status_uuid, 'status': status}

    def sign_file_sf(self,xmldata):
        pac_params_obj = self.env['params.pac']
        f = False
        msg = ''
        cfdi_xml = False
        pac_ids = pac_params_obj.search(
            [('method_type', '=', 'pac_sf_firmar'),
             ('company_id', '=', self.company_id.id),
             ('active', '=', True)
             ],
            limit=1)
        if not pac_ids:
            raise UserError(
                _('Not found information from web services of PAC'
                  'Verify that the configuration of PAC is correct')
            )
        user = pac_ids.user
        password = pac_ids.password
        wsdl_url = pac_ids.url_webservice
        namespace = pac_ids.namespace
        #cfd_data = base64.decodestring(xmldata)
        #raise UserError("",str(cfd_data))
        wsdl_client = Client(wsdl_url)
        zip = False
        params = [user, password, xmldata.decode(), zip]
        resultado = wsdl_client.service.timbrar(*params)
        #resultado = wsdl_client.service.timbrar(user, password, fdata.decode() , zip)
        #clientess = Client(pac_ids.url_webservice)
        #timbrado =  clientess.service.timbrar(pac_ids.user,pac_ids.password,xmldata)
        mensaje = resultado['mensaje']#.encode('UTF-8')
        codigo_timbrado = resultado['status'] or ''
        codigo_validacion = resultado['resultados'] and resultado['resultados'][0]['status'] or ''
        validacion_mesage = resultado['resultados'] and resultado['resultados'][0]['mensaje'] or ''

        #raise UserError( str( type(codigo_timbrado)  ))
        if codigo_timbrado == 311 or codigo_validacion == 311:
            raise UserError(
                _('Unauthorized.\nCode 311')
            )
        elif codigo_timbrado == 312 or codigo_validacion == 312:
            raise UserError(
                _('Failed to consult the SAT.\nCode 312')
            )
        elif codigo_timbrado == 200 and codigo_validacion == 200 or codigo_validacion == 307:
            uuid=resultado['resultados'][0]['uuid'] or ''

            fecha_timbrado =str(resultado['resultados'][0]['fechaTimbrado'])#.today()#.strptime('%Y-%m-%d %H:%M:%S')

            

            #raise UserError(   str(fecha_timbrado[:19])  )
            cfdi_data = {
                'cfdi_sello':resultado['resultados'][0]['selloSAT'] or False,
                'cfdi_no_certificado': resultado['resultados'][0]['certificadoSAT'] or False,
                'cfdi_cadena_original': resultado['resultados'][0]['cadenaOriginal'] or False,
                'cfdi_fecha_timbrado':str(resultado['resultados'][0]['fechaTimbrado']).replace('+00:00','') or False,
                'cfdi_folio_fiscal': resultado['resultados'][0]['uuid'] or '',
                'cfdi_xml':str(base64.b64decode(resultado['resultados'][0]['cfdiTimbrado'] or ''),encoding='utf-8')
            }
            cfdi_xml =cfdi_data['cfdi_xml'] #base64.decodestring(resultado['resultados'][0]['cfdiTimbrado']) #cfdi_data.pop('cfdi_xml')
            #raise UserError("h",str( cfdi_data ))
            parsedata = xml.dom.minidom.parseString( cfdi_xml )
            #raise UserError("h",str( parsedata ))
            complemento = parsedata.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
            rfcprov = complemento.attributes['RfcProvCertif'].value
            cfdi_data.update({'rfcprovcertif':rfcprov})

            self.payment_id.write(cfdi_data)
            self.write({'uuid': uuid})
            # Codifica el XML para almacenarlo
            #f = base64.decodestring(resultado['resultados']['cfdiTimbrado']) or ''
            msg=mensaje
            #msg += string.join([mensaje, ". Folio Fiscal ", uuid, "."])
        else:
            # El CFDI no ha sido timbrado
            raise UserError(
                _('Codigo de Error: %s. \n Mensaje: %s.' %
                  (codigo_validacion, validacion_mesage))#(resultado['codigo'], mensaje))                
            )
        return {'file': f, 'msg': msg, 'cfdi_xml': cfdi_xml}