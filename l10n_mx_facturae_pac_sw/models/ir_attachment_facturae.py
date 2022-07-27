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
    from suds.client import Client # from SOAPpy import WSDL
except:
    logger.error("Package suds.client missed")

# new libraris
import requests
import json
import traceback
import random


class IrAttachmentFacturaeMx(models.Model):
    _inherit = 'ir.attachment.facturae.mx'

    # @api.multi
    def _get_type(self):
        types=super(IrAttachmentFacturaeMx, self)._get_type()
        types.extend([('cfdi32_pac_sw', 'CFDI 3.3 SW sapien')])
        return types

    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(IrAttachmentFacturaeMx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_sw': self.sw_sign})
        return factura_mx_type__fc

    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(IrAttachmentFacturaeMx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_sw': self.sw_cancel})
        return factura_mx_type__fc

    type = fields.Selection('_get_type', string='Type')
    
    # @api.multi
    def sw_cancel(self):
        msg = ''
        pac_params_obj = self.env['params.pac']
        invoice_obj = self.env['account.invoice']
        for ir_attachment_facturae_mx_id in self:
            status = False
            invoice = ir_attachment_facturae_mx_id.invoice_id
            pac_params_ids = pac_params_obj.search([
                ('method_type', '=', 'pac_sw_cancelar'),
                ('company_id', '=', self.company_id.id),#invoice.company_emitter_id.id),
                ('active', '=', True),
            ], limit=1)
            status_uuid = False
            if pac_params_ids:
                pac_params_id = pac_params_ids
                file_globals = invoice._get_file_globals()
                user = pac_params_id.user
                password = pac_params_id.password
                wsdl_url = pac_params_id.url_webservice
                namespace = pac_params_id.namespace
                fname_cer_no_pem = file_globals['fname_cer']
                cerCSD = fname_cer_no_pem and base64.encodestring(open(fname_cer_no_pem, "r").read()) or ''
                fname_key_no_pem = file_globals['fname_key']
                keyCSD = fname_key_no_pem and base64.encodestring(open(fname_key_no_pem, "r").read()) or ''
                zip = False  # Validar si es un comprimido zip, con la extension del archivo
                contrasenaCSD = file_globals.get('password', '')
                uuids = invoice.cfdi_folio_fiscal  # cfdi_folio_fiscal
                params = [user, password, uuids, cerCSD, keyCSD, contrasenaCSD]
                headers = {'user': user , 'password': password, 'Cache-Control': "no-cache"}
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
                    # respon = requests.request("POST", wsdl_url + "/cfdi33/cancel/"+invoice.address_issued_id.vat_split+"/" + uuids, headers=headers)
 
                    payload = "{ \"uuid\": \"" + uuids + "\",  \"password\": \"" + password + "\", \"rfc\": \"" + invoice.address_issued_id.vat_split + "\",    \"b64Cer\": \"" + cerCSD + "\",  \"b64Key\": \"" + keyCSD + "\"}"
                    headers = {
                        'Authorization': "bearer " + token,
                        'Content-Type': "application/json"
                    }
                    respon = requests.request("POST", wsdl_url + "/cfdi33/cancel/csd", data=payload, headers=headers)

                    if respon.status_code == 200:
                        datas=json.loads(respon.text)
                        if datas['status'] == 'success':
                            status_uuid = respon.status_code
                            folio_cancel = datas['data'] and datas['data']['uuid'] or ''
                            status = True
                            msg += ('\n- The process of cancellation\
                                has completed correctly.\n- The uuid cancelled is:\
                                ') + str(folio_cancel)
                            invoice.write({
                                'cfdi_fecha_cancelacion': time.strftime('%Y-%m-%d %H:%M:%S'), 
                                'state_sat': 'Cancelado', 
                                'state_cfdi': 3
                            })
                            
                        elif datas['status']=='error':
                            raise UserError("Error",str(datas['message'])+'Detale:'+str(datas['messageDetail']))
                    else:
                        resul = json.loads(respon.text)
                        raise UserError("Error",str(resul))

            else:
                msg = _('Not found information of webservices of PAC, verify that the configuration of PAC is correct')
        return {'message': msg, 'status_uuid': status_uuid, 'status': status}

    # @api.multi
    def sw_sign(self, fdata=None):
        context = self._context.copy()
        invoice_obj = self.env['account.move']
        pac_params_obj = invoice_obj.env['params.pac']

        for ir_attachment_facturae_mx_id in self:
            invoice = ir_attachment_facturae_mx_id.move_id#invoice_id
            comprobante = invoice._get_type_sequence()
            cfd_data = base64.b64decode(fdata or invoice_obj.fdata).decode("utf-8", "ignore")
            # raise UserError( str(  cfd_data ))
            # raise UserError("timbrado===="+str(cfd_data ))
            xml_res_str = xml.dom.minidom.parseString(cfd_data)
            xml_res_addenda = invoice_obj.add_addenta_xml(xml_res_str, comprobante)
            xml_res_str_addenda = xml_res_addenda.toxml('UTF-8')
            compr = xml_res_addenda.getElementsByTagName(comprobante)[0]
            date = compr.getAttribute('Fecha')
            date_format = datetime.strptime(
                date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
            context.update({'date': date_format})
            invoice_ids = [invoice.id]
            file = False
            msg = ''
            cfdi_xml = False
            pac_params_ids = pac_params_obj.search([
                ('method_type', '=', 'pac_sw_firmar'), (
                    'company_id', '=', 1),
                    ('active', '=', True)], limit=1)
            if pac_params_ids:
                pac_params =pac_params_ids 
                user = pac_params.user
                password = pac_params.password
                wsdl_url = pac_params.url_webservice
                namespace = pac_params.namespace
                if True:  # if wsdl_client:
                    file_globals = invoice._get_file_globals()
                    fname_cer_no_pem = file_globals['fname_cer']
                    cerCSD = fname_cer_no_pem and bytes(open(fname_cer_no_pem,"r").read().encode('utf-8')) or ''
                    fname_key_no_pem = file_globals['fname_key']
                    keyCSD = fname_key_no_pem and base64.b64encode(open(fname_key_no_pem,"r").read().encode('utf-8')) or ''
                    cfdi = str(base64.b64encode(xml_res_str_addenda), encoding='utf-8')
                    zip = False 
                    contrasenaCSD = file_globals.get('password', '')
                    params = [user, password, cfdi, zip]
                    # try:
                    #     wsdl_client = Client(wsdl_url)
                    #     resultado = wsdl_client.service.timbrar(user, password, cfdi, zip)
                    # except Exception as e:
                    #     raise ValidationError(str(e))
                    headers = {'user': user , 'password': password, 'Cache-Control': "no-cache"}
                    conexion_authen = requests.request("POST", (wsdl_url + "/security/authenticate"), headers=headers, verify = True, timeout=300)
                    if conexion_authen.status_code == 200:
                        res = json.loads(conexion_authen.text)
                        status = res['status']
                        token = res['data']['token']
                        version = 'v4'
                        bs64 = "/b64"
                        boundary = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
                        payload = "--" + boundary + "\r\nContent-Type: text/xml\r\nContent-Transfer-Encoding: binary\r\nContent-Disposition: form-data; name=\"xml\"; filename=\"xml\"\r\n\r\n" + str(cfdi) + "\r\n--" + boundary + "-- "
                        headers = {
                                'Authorization': "bearer " + token,
                             'Content-Type': "multipart/form-data; boundary=\"" + boundary + "\""
                        }
                        respon = requests.request("POST", wsdl_url + "/cfdi33/stamp/" + version + "/" + bs64, data=payload, headers=headers,verify = True, timeout = 300)
                        # variables timbrado
                        # raise UserError("Errr"+ str( json.loads(respon.text)   ))
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
                            
                            cfdi_data = {
                                # 'cfdi_cbb': datas['data']['qrCode'] or False,
                                'cfdi_sello': datas['data']['selloSAT'] or False,
                                'cfdi_no_certificado':datas['data']['noCertificadoSAT'] or False,
                                'cfdi_cadena_original': datas['data']['cadenaOriginalSAT'] or False,
                                'cfdi_fecha_timbrado': fecha_timbrado,
                                'cfdi_xml': str(base64.b64decode(datas['data']['cfdi'] or False), encoding='utf-8'), #base64.decodestring(datas['data']['cfdi']) or False,  # este se necesita en uno que no es base64
                                'cfdi_folio_fiscal':  datas['data']['uuid'] or '',
                            }

                            if cfdi_data.get('cfdi_xml', False):
                                url_pac = '</"%s"><!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://solucionfactible.com/cfdi/00001000000102699425.zip-->' % (
                                    comprobante)
                                # cfdi_data['cfdi_xml'] = cfdi_data['cfdi_xml'].replace('</"%s">' % (comprobante), url_pac)
                                # file = base64.encodestring(cfdi_data['cfdi_xml'] or '')
                                parsedata = xml.dom.minidom.parseString( cfdi_data['cfdi_xml'] )
                                complemento = parsedata.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
                                rfcprov = complemento.attributes['RfcProvCertif'].value
                                cfdi_data.update({'rfcprov': rfcprov})
                                #State cfdi
                                # if invoice.state_sat == 'Vigente' or invoice.state_sat == 'Cancelado':
                                #     cfdi_data.update({'state_cfdi': 2})
                                # else:
                                #     cfdi_data.update({'state_cfdi': 1})

                                cfdi_xml = cfdi_data.pop('cfdi_xml')
                            if cfdi_xml:
                                invoice.write(cfdi_data)
                                cfdi_data['cfdi_xml'] = cfdi_xml
                            else:
                                msg += _(u"Can't extract the file XML of PAC")

                        elif respon.status_code == 400:
                            datas=json.loads(respon.text)
                            # nomina_id = payslip_obj.browse(cr, uid, fdata.get('payslip_id'), context=context)
                            # raise UserError("UserError",str(datas['messageDetail']))
                            if datas:                            
                                #msg = "Error: " + str((datas['message']).encode('utf-8').decode('ascii','ignore') or 'Sin resultados') + " Detalles: " + str((datas['messageDetail']).encode('utf-8').decode('ascii','ignore') or 'Sin resultados' )
                                msg = "Error: " + str(datas['message'] or 'Sin resultados') + " Detalles: " + str(datas['messageDetail'] or 'Sin resultados' )                                
                                raise UserError(_("%s")%(msg))

                        else:
                            msg = "Codigo de Error:" + str(respon.status_code) + str(respon.text)
                            raise UserError(_("%s")%(msg))

                    elif conexion_authen.status_code == 401:
                        msg = "Acceso Denegado"
                        raise UserError(("Error de autorizacion, %s")%(msg))

                    else:
                        msg = "Acceso Denegado"
                        raise UserError(_("%s")%(msg))
                        # datas=json.loads(respon.text)
                        # raise UserError("restados xml",str(respon.status_code))
                        # raise  UserError("restados",str( datas ))
                    # raise  UserError("params",str( conexion_authen ))
            else:
                raise UserError(_('Warning!\nNot found information from web services of PAC,\n  verify that the configuration of PAC is correct'))
            return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml}

