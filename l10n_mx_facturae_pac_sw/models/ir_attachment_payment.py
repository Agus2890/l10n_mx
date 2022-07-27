# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
import logging
import string
import base64
import xmltodict
from odoo.exceptions import UserError
# from SOAPpy import WSDL
from odoo import models, fields, api
from odoo.tools.translate import _
import codecs
import xml.dom.minidom
import time
from requests import Request, Session, exceptions
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)

try:
    # from SOAPpy import WSDL
    from suds.client import Client
except:
    logger.error("Package suds.client missed")

# new libraris
import requests
import json
import traceback
import random


class IrAttachmentPaymentMx(models.Model):
    _inherit = 'ir.attachment.payment.mx'

    # @api.model
    def _get_type(self):
        types=super(IrAttachmentPaymentMx, self)._get_type()
        types.extend([('cfdi32_pac_sw', 'CFDI 3.3 SW sapien')])
        return types

    type = fields.Selection('_get_type',string='Type')

    def get_driver_fc_sign(self):
        drivers = super(IrAttachmentPaymentMx, self).get_driver_fc_sign()
        drivers.update({'cfdi32_pac_sw': self.sw_sign})
        return drivers

    def get_driver_fc_cancel(self):
        drivers = super(IrAttachmentPaymentMx, self).get_driver_fc_cancel()
        drivers.update({'cfdi32_pac_sw': self.sw_cancel})
        return drivers

    # @api.multi
    def sw_cancel(self):
        msg = ''
        pac_params_obj = self.env['params.pac']
        for ir_attachment_payment in self:
            status = False
            payment = ir_attachment_payment.payment_id
            pac_params_ids = pac_params_obj.search([
                ('method_type', '=', 'pac_sw_cancelar'),
                ('company_id', '=', self.company_id.id),#payment.company_emitter_id.id),
                ('active', '=', True),
            ], limit=1)
            status_uuid = False
            if pac_params_ids:
                pac_params_id = pac_params_ids
                file_globals = self._get_file_globals()

                user = pac_params_id.user
                password = pac_params_id.password
                wsdl_url = pac_params_id.url_webservice
                namespace = pac_params_id.namespace
                fname_cer_no_pem = file_globals['fname_cer_no_pem'] #file_globals['fname_cer']
                cerCSD = base64.b64encode(open(fname_cer_no_pem, "rb").read()).decode('utf-8') #cerCSD = fname_cer_no_pem and base64.encodestring(open(fname_cer_no_pem, "r").read()) or ''
                fname_key_no_pem = file_globals['fname_key_no_pem'] #file_globals['fname_key']
                keyCSD = base64.b64encode(open(fname_key_no_pem, "rb").read()).decode('utf-8') #keyCSD = fname_key_no_pem and base64.encodestring(open(fname_key_no_pem, "r").read()) or ''
                
                zip = False  # Validar si es un comprimido zip, con la extension del archivo
                contrasenaCSD = file_globals.get('password', '')
                uuids = payment.cfdi_folio_fiscal  # cfdi_folio_fiscal
                params = [user, password, uuids, cerCSD, keyCSD, contrasenaCSD]
                headers = {'user': user, 'password': password, 'Cache-Control': "no-cache"}
                conexion_authen = requests.request("POST", (wsdl_url + "/security/authenticate"), headers=headers, verify=True, timeout=300)

                if conexion_authen.status_code == 200:
                    res = json.loads(conexion_authen.text)
                    status = res['status']
                    token = res['data']['token']

                    # version = 'v4'
                    # bs64 = "/b64"
                    # boundary = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
                    # headers = {
                    #         'Authorization': "bearer " + token,
                    #      'Content-Type': "application/json"
                    # }
                    # respon = requests.request("POST", wsdl_url + "/cfdi33/cancel/"+payment.company_id.partner_id.vat_split+"/" + uuids, headers=headers)

                    payload = "{ \"uuid\": \"" + uuids + "\",  \"password\": \"" + contrasenaCSD + "\", \"rfc\": \"" + payment.company_id.partner_id.vat_split + "\", \"b64Cer\": \"" + cerCSD + "\", \"b64Key\": \"" + keyCSD + "\"}"
                    headers = {
                        'Authorization': "bearer " + token,
                        'Content-Type': "application/json"
                    }
                    respon = requests.request("POST", wsdl_url + "/cfdi33/cancel/csd", data=payload, headers = headers)

                    if respon.status_code == 200:
                        datas=json.loads(respon.text)
                        if datas['status'] == 'success':
                            status_uuid = respon.status_code
                            folio_cancel = datas['data'] and datas['data']['uuid'] or ''
                            status = True
                            msg += ('\n- The process of cancellation\
                                has completed correctly.\n- The uuid cancelled is:\
                                ') + str(folio_cancel)
                            payment.write({'cfdi_fecha_cancelacion': time.strftime('%Y-%m-%d %H:%M:%S')})
                            
                        elif datas['status']=='error':
                            raise UserError("Error",str(datas['message'])+'Detale:'+str(datas['messageDetail']))
                    else:
                        res = json.loads(respon.text)
                        raise UserError(_("Error %s")%(res))
                    
            else:
                msg = _('Not found information of webservices of PAC, verify that the configuration of PAC is correct')
        return {'message': msg, 'status_uuid': status_uuid, 'status': status}

    # @api.multi
    def sw_sign(self, xmldata):
        pac_params_obj = self.env['params.pac']
        payment = self.payment_id
        file = False
        msg = ''
        cfdi_xml = False
        pac_ids = pac_params_obj.search([
            ('method_type', '=', 'pac_sw_firmar'), (
                'company_id', '=', 1),
                ('active', '=', True)], limit=1)
        if not pac_ids:
            raise UserError(
                _('Not found information from web services of PAC'
                  'Verify that the configuration of PAC is correct')
            )

        user = pac_ids.user
        password = pac_ids.password
        wsdl_url = pac_ids.url_webservice
        namespace = pac_ids.namespace

        cfd_data = base64.b64decode(xmldata).decode("utf-8", "ignore") 
        xml_res_str = xml.dom.minidom.parseString(cfd_data)
        cfd_data = xml_res_str.toxml('UTF-8')
        # raise UserError(str( cfd_data))
        zip = False
        params = [user, password, cfd_data, zip]
        headers = {'user': user , 'password': password, 'Cache-Control': "no-cache"}
        conexion_authen = requests.request("POST", (wsdl_url + "/security/authenticate"), headers=headers, verify = True, timeout=300)
        if conexion_authen.status_code == 200:
            res = json.loads(conexion_authen.text)
            status = res['status']
            token = res['data']['token']
            version = 'v4'
            cfdi = str(base64.b64encode(cfd_data), encoding='utf-8')
            bs64 = "/b64"
            boundary = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
            payload = "--" + boundary + "\r\nContent-Type: text/xml\r\nContent-Transfer-Encoding: binary\r\nContent-Disposition: form-data; name=\"xml\"; filename=\"xml\"\r\n\r\n" + str(cfdi) + "\r\n--" + boundary + "-- "
            headers = {
                    'Authorization': "bearer " + token,
                 'Content-Type': "multipart/form-data; boundary=\"" + boundary + "\""
            }
            respon = requests.request("POST", wsdl_url + "/cfdi33/stamp/" + version + "/" + bs64, data=payload, headers=headers, verify=True, timeout=300)
            # variables timbrado
            datas = False

            if respon.status_code == 200:
                # respuesta del web Service
                datas=json.loads(respon.text)                        
                fecha_timbrado = datas['data']['fechaTimbrado'] or False
                fecha_timbrado = fecha_timbrado and time.strftime(
                      '%Y-%m-%d %H:%M:%S', time.strptime(
                fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                fecha_timbrado = fecha_timbrado and datetime.strptime(
                fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(
                           hours=6) or False
                
                cfdi_xml = str(base64.b64decode(datas['data']['cfdi'] or ''), encoding='utf-8')                    

                cfdi_data = {
                    # 'cfdi_cbb': datas['data']['qrCode'] or False,
                    'cfdi_qrcode': datas['data']['qrCode'] or False,
                    'cfdi_sello': datas['data']['selloSAT'] or False,
                    'cfdi_no_certificado':datas['data']['noCertificadoSAT'] or False,
                    'cfdi_cadena_original': datas['data']['cadenaOriginalSAT'] or False,
                    'cfdi_fecha_timbrado': fecha_timbrado,
                    'cfdi_xml': str(base64.b64decode(datas['data']['cfdi'] or False, encoding='utf-8')),  # este se necesita en uno que no es base64
                    'cfdi_folio_fiscal':  datas['data']['uuid'] or '',
                }

                if cfdi_data.get('cfdi_xml', False):
                    xml_data = str(base64.b64decode(cfdi_data['cfdi_xml'] or ''), encoding='utf-8')
                    parsedata = xml.dom.minidom.parseString(xml_data)
                    complemento = parsedata.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
                    rfcprov = complemento.attributes['RfcProvCertif'].value
                    cfdi_data.update({'rfcprovcertif': rfcprov})
 

                    cfdi_xml = cfdi_data.pop('cfdi_xml')
                if cfdi_xml:
                    self.payment_id.write(cfdi_data)
                    self.payment_id.write({'cfdi_xml':cfdi_xml.encode("utf-8", "ignore") })
                    cfdi_xml = cfdi_xml#cfdi_data['cfdi_xml']
                    # msg=mensaje_resul
                
            elif respon.status_code == 400:
                datas=json.loads(respon.text)
                # nomina_id = payslip_obj.browse(cr, uid, xmldata.get('payslip_id'), context=context)
                # raise UserError("Warning",str(datas['messageDetail']))
                if datas:                            
                    #msg = "Error: " + str((datas['message']).encode('utf-8').decode('ascii','ignore') or 'Sin resultados') + " Detalles: " + str((datas['messageDetail']).encode('utf-8').decode('ascii','ignore') or 'Sin resultados' )
                    msg = "Error: " + str(datas['message'] or 'Sin resultados') + " Detalles: " + str(datas['messageDetail'] or 'Sin resultados' )                                
                    raise UserError(_("%s")%(msg))

            else:
                msg = "Codigo de Error:"+ str(respon.status_code)
                raise UserError(("%s")%(msg))

        elif conexion_authen.status_code == 401:
            msg = "Acceso Denegado"
            raise UserError(_("Error de autorizacion, %s")%(msg))

        else:
            raise UserError(_('Warning!\nNot found information from web services of PAC,\n  verify that the configuration of PAC is correct'))
        return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml}