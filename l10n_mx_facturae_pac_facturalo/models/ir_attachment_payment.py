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
        types.extend([('cfdi_pac_xpd','CFDI 4.0 Expide tu factura')])
        return types

    type=fields.Selection('_get_type',string='Type')

    def get_driver_fc_sign(self):
        drivers = super(IrAttachmentPaymentMx, self).get_driver_fc_sign()
        drivers.update({'cfdi_pac_xpd': self.sign_file_xpd})
        return drivers

    def get_driver_fc_cancel(self):
        drivers = super(IrAttachmentPaymentMx, self).get_driver_fc_cancel()
        drivers.update({'cfdi32_pac_sf': self.cancel_file_sf})
        return drivers

    def sign_file_xpd(self,xmldata):

        pac_params_obj = self.env['params.pac']
        f = False
        msg = ''
        cfdi_xml = False
        pac_ids = pac_params_obj.search(
            [('method_type', '=', 'pac_xpd_firmar'),
             ('company_id', '=', self.company_id.id),
             ('active', '=', True)
             ],
            limit=1)
        if not pac_ids:
            raise UserError(
                _('Not found information from web services of PAC'
                  'Verify that the configuration of PAC is correct')
            )
        #user = pac_ids.user
        #password = pac_ids.password
        #wsdl_url = pac_ids.url_webservice
        #namespace = pac_ids.namespace
        #cfd_data = base64.decodestring(xmldata)
        #raise UserError("",str(cfd_data))
        wsdl_client = Client(pac_ids.url_webservice)
        #zip = False
        params = [pac_ids.user, pac_ids.password,xmldata.decode()]
        resultado = wsdl_client.service.timbrar(*params)
        #raise UserError(str(resultado))
        
        mensaje = resultado['mensaje']#.encode('UTF-8')
        codigo_timbrado = resultado['codigo'] or ''
        if codigo_timbrado == "200":
            timbre = resultado['timbre'].encode('UTF-8')
            parsedata = xml.dom.minidom.parseString(timbre)
            complemento = parsedata.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
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
                                     str(fecha).replace('T',' '),
                                     self.payment_id.sello,
                                     str(no_certificado)])
                cadena = "||{0}||".format(cadena)
            except:
               cadena = ''
            cfdi_data = {
                'cfdi_sello':selloSAT or False,
                'cfdi_no_certificado': no_certificado or False,
                'cfdi_cadena_original': cadena or False,
                'cfdi_fecha_timbrado':str(fecha).replace('T',' ') or False,
                'cfdi_folio_fiscal': uuid or '',
                #'cfdi_xml':str(base64.b64decode(timbre or ''),encoding='utf-8'),
                'rfcprovcertif':rfcprov
            }
            cfdi_xml =timbre.decode("utf-8", "ignore")
            self.payment_id.write(cfdi_data)
            self.write({'uuid': uuid})
            msg=mensaje
        else:
            # El CFDI no ha sido timbrado
            raise UserError(
                _('Codigo de Error: %s. \n Mensaje: %s.' %
                  (codigo_timbrado, mensaje))#(resultado['codigo'], mensaje))                
            )
        return {'file': f, 'msg': msg, 'cfdi_xml': cfdi_xml}