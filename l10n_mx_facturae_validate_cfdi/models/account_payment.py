# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)
try:
    import xmltodict
except:
    _logger.error(
        'Execute "sudo pip install xmltodict" to use '
        'l10n_mx_facturae_report module.')

_SOAPENV = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <tem:Consulta>
                                <tem:expresionImpresa>?re=%s&amp;rr=%s&amp;tt=%s&amp;id=%s</tem:expresionImpresa>
                            </tem:Consulta>
                        </soapenv:Body>
                    </soapenv:Envelope>"""


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def validate_xml_sat(self):
        #for payment in self.browse(cr, uid, ids, context=context):
        for payment in self:
            if payment.cfdi_folio_fiscal:
                if not payment.partner_id.vat_split:
                    raise UserError("",_('Parner sin  RFC'))
                data = _SOAPENV % (payment.company_id.partner_id.vat_split,payment.partner_id.vat_split,payment.amount_total,payment.cfdi_folio_fiscal)
                url ="https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc";
                headers = {
                    'Content-Type':'text/xml;charset=utf-8',
                    'SOAPAction':'http://tempuri.org/IConsultaCFDIService/Consulta',
                    'User-Agent':'Mozilla/5.0',
                    'Content-length':data
                }
                response = requests.post(url,data=data,timeout=60,headers=headers)
                xml_res= response.text.encode('utf-8', 'ignore')
                res = xmltodict.parse( xml_res )
                
                code_state=res['s:Envelope']['s:Body']['ConsultaResponse']['ConsultaResult']['a:CodigoEstatus']
                is_cancel_sat=res['s:Envelope']['s:Body']['ConsultaResponse']['ConsultaResult']['a:EsCancelable']
                state_sat=res['s:Envelope']['s:Body']['ConsultaResponse']['ConsultaResult']['a:Estado']
                state_cancel_sat=res['s:Envelope']['s:Body']['ConsultaResponse']['ConsultaResult']['a:EstatusCancelacion']
                payment.write({'code_state':code_state,'is_cancel_sat':is_cancel_sat,'state_sat':state_sat,'state_cancel_sat':state_cancel_sat})

    code_state = fields.Char(string="Comprobante", copy=False)
    is_cancel_sat = fields.Char(string="Es Cancelable ?", copy=False)
    state_sat = fields.Char(string="Estatus SAT", copy=False)
    state_cancel_sat = fields.Char(string="Estatus Cancelacion", copy=False)
    state_cfdi = fields.Selection([
        (0, 'Sin Timbrar'),
        (1, 'Timbrado'),
        (2, 'Retimbrado'),
        (3, 'Cancelado'),
        ], 'Estatus CFDI', default=0, copy=False,
        help="Indica el estado fiscal del documento.")

    @api.multi
    def action_view_payment_cfdi(self):
        self.ensure_one()
        module = "l10n_mx_payment_cfdi"
        view = self.env.ref('%s.view_ir_attachment_payment_mx_tree' % module)
        return {
            'name': 'action.ir.attachment.payment.mx',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'ir.attachment.payment.mx',
            'view_id': view.id,
            # 'target': 'new',
            'type': 'ir.actions.act_window',
        }
