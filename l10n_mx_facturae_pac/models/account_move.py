# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
import tempfile
import os
import codecs
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_facturae_invoice_dict_data(self):
        datas = super(AccountMove, self)._get_facturae_invoice_dict_data()
        type_inv = self.journal_id.type_cfdi or 'cfd22'
        for data in datas:
            comprobante = data['Comprobante']
            if 'cfdi32' in type_inv:
                comprobante = data['Comprobante']
                rfc = comprobante['Emisor']['Rfc']
                nombre = comprobante['Emisor']['Nombre']
                RegimenFiscal=comprobante['Emisor']['RegimenFiscal']
                
                rfc_receptor = comprobante['Receptor']['Rfc']
                nombre_receptor = comprobante['Receptor']['Nombre']
                usicfdi = comprobante['Receptor']['UsoCFDI']

                dict_emisor = dict({'Rfc': rfc,
                                    'Nombre': nombre,
                                    'RegimenFiscal':RegimenFiscal
                                   
                                    })
                dict_receptor = dict({'Rfc': rfc_receptor,
                                      'Nombre': nombre_receptor,
                                      'UsoCFDI':usicfdi,
                                      'DomicilioFiscalReceptor':self.partner_id.zip,
                                      'RegimenFiscalReceptor':self.partner_id.property_account_position_id.clave
                                      })
                list_conceptos = []

                for concepto in comprobante['Conceptos']:
                    list_conceptos.append(dict({'cfdi:Concepto':
                                                concepto['Concepto']}))
               
                dict_impuestos = comprobante['cfdi:Impuestos']
                comprobante.pop('cfdi:Impuestos')
                
                comprobante.update({'cfdi:Emisor': dict_emisor,
                                    'cfdi:Receptor': dict_receptor,
                                    'cfdi:Conceptos': list_conceptos,
                                    'cfdi:Impuestos': dict_impuestos,
                                    })

                comprobante.pop('Emisor')
                # comprobante.pop('cfdi:Impuestos')
                comprobante.pop('Conceptos')
                comprobante.pop('Receptor')
                # comprobante.pop('xsi:schemaLocation')
                comprobante.update({'xsi:schemaLocation':"http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd"})

                dict_comprobante = comprobante
                # raise UserError(str(dict_comprobante))
                data.pop('Comprobante')
                data.update(dict({'cfdi:Comprobante': dict_comprobante}))
        return datas

    # def _get_facturae_invoice_xml_data(self):
    #     context = dict(self._context or {})        
    #     type_inv = self.journal_id.type_cfdi or 'cfd22'
    #     # raise UserError(_("Valores %s")%(context))    
    #     if 'cfdi32' in type_inv:# or 'cfdi33_facturehoy' in type_inv:
    #         comprobante = 'cfdi:Comprobante'
    #         emisor = 'cfdi:Emisor'
    #         receptor = 'cfdi:Receptor'
    #         concepto = 'cfdi:Conceptos'
    #     else:   
    #         comprobante = 'cfdi:Comprobante'
    #         emisor = 'cfdi:Emisor'
    #         receptor = 'cfdi:Receptor'
    #         concepto = 'cfdi:Conceptos'

    #     data_dict = self._get_facturae_invoice_dict_data()#[0]
    #     # raise UserError(_("Valores data_dict %s")%(data_dict))
    #     doc_xml = self.dict2xml(
    #             # {comprobante: data_dict.get(comprobante)}
    #             {'Comprobante': data_dict.get('Comprobante')}
    #         )
    #     # raise UserError(_("Valores doc_xml %s")%(doc_xml))
    #     invoice_number = "sn"
    #     (fileno_xml, fname_xml) = tempfile.mkstemp(
    #         '.xml', 'odoo_' + (invoice_number or '') + '__facturae__')
    #     fname_txt = fname_xml + '.txt'
    #     # Write xml file with proper encoding
    #     address_invoice_parent = (
    #         self.company_id and
    #         self.company_id.address_invoice_parent_company_id or
    #         False
    #     )
    #     # raise UserError(_("Valores %s")%(address_invoice_parent))
    #     nodeComprobante = doc_xml.getElementsByTagName('cfdi:Emisor')[0]
    #     nodeComprobante.setAttribute("Nombre", address_invoice_parent.name)
    #     #raise UserError("",str(doc_xml.toxml('UTF-8')  ))
    #     #with codecs.open(fname_xml, 'w', encoding='UTF-8') as f:
    #     #    doc_xml.writexml(f,encoding="utf-8")

    #     with open(fname_xml,'w') as f:
    #         f.write(doc_xml.toxml("utf-8"))

    #     f = open(fname_xml, 'w')
    #     doc_xml.writexml(f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')  

    #     (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'odoo_' + (
    #         invoice_number or '') + '__facturae_txt_md5__')
    #     os.close(fileno_sign)

    #     context.update({
    #         'fname_xml': fname_xml,
    #         'fname_txt': fname_txt,
    #         'fname_sign': fname_sign,
    #     })
    #     context.update(self._get_file_globals())#context.update(self.with_context(context)._get_file_globals())#
    #     fname_txt, txt_str = self.with_context(context)._xml2cad_orig()
    #     raise UserError(_("Valores context.update %s")%(txt_str))    
    #     data_dict['cadena_original'] = txt_str
    #     raise UserError(_("Valores cadena_original %s")%(data_dict['cadena_original']))    
    #     context.update({
    #         'cadena_original': txt_str
    #     })
    #     raise UserError(_("Valores txt_str %s")%(txt_str))    
    #     if not txt_str:
    #         raise UserError(
    #             _("Error in Original String!\n"
    #               "Can't get the string original of the voucher.\n"
    #               "Ckeck your configuration.")
    #         )
    #     # TODO: Is this validation needed?
    #     if not data_dict[comprobante].get('Folio', ''):
    #         raise UserError(
    #             _("Error in Folio!\n"
    #               "Can't get the folio of the voucher.\n"
    #               "Before generating the XML, click on the button, "
    #               "generate invoice.\nCkeck your configuration.\n")
    #         )

    #     context.update({'fecha': data_dict[comprobante]['Fecha']})
    #     sign_str = self.with_context(context)._get_sello()
    #     if not sign_str:
    #         raise UserError(
    #             _("Error in Stamp !\n"
    #               "Can't generate the stamp of the voucher.\n"
    #               "Ckeck your configuration.")
    #         )

    #     nodeComprobante = doc_xml.getElementsByTagName(comprobante)[0]
    #     nodeComprobante.setAttribute("Sello", sign_str)
    #     data_dict[comprobante]['Sello'] = sign_str

    #     noCertificado = self._get_noCertificado(context['fname_cer'])
    #     if not noCertificado:
    #         raise UserError(
    #             _("Error in No. Certificate !\n"
    #               "Can't get the Certificate Number of the voucher.\n"
    #               "Ckeck your configuration.")
    #         )
    #     nodeComprobante.setAttribute("NoCertificado", noCertificado)
    #     data_dict[comprobante]['NoCertificado'] = noCertificado

    #     cert_str = self._get_certificate_str(context['fname_cer'])
    #     if not cert_str:
    #         raise UserError(
    #             _("Error in Certificate!\n"
    #               "Can't get the Certificate Number of the voucher.\n"
    #               "Ckeck your configuration.")
    #         )
    #     cert_str = cert_str.replace(' ', '').replace('\n', '')
    #     nodeComprobante.setAttribute("Certificado", cert_str)
    #     data_dict[comprobante]['Certificado'] = cert_str

    #     x = doc_xml.documentElement
    #     nodeReceptor = doc_xml.getElementsByTagName(receptor)[0]
    #     nodeConcepto = doc_xml.getElementsByTagName(concepto)[0]
    #     x.insertBefore(nodeReceptor, nodeConcepto)
    #     self.write_cfd_data(data_dict)

    #     if context.get('type_data') == 'dict':
    #         return data_dict
    #     if context.get('type_data') == 'xml_obj':
    #         return doc_xml
    #     data_xml = doc_xml.toxml('UTF-8')
    #     data_xml = codecs.BOM_UTF8 + data_xml
    #     #raise UserError("",str(data_xml))
    #     fname_xml = (data_dict[comprobante][emisor]['Rfc'] or '') + '_' + (
    #         data_dict[comprobante].get('Serie', '') or '') + '_' + (
    #         data_dict[comprobante].get('Folio', '') or '') + '.xml'
    #     data_xml = data_xml.replace(
    #         '<?xml version="1.0" encoding="UTF-8"?>',
    #         '<?xml version="1.0" encoding="UTF-8"?>\n')
    #     return fname_xml, data_xml

    def _get_facturae_invoice_xml_data_old(self):
        context = dict(self._context or {})  
        type_inv = self.journal_id.type_cfdi or 'cfd22'
        if 'cfdi32' in type_inv:# or 'cfdi33_facturehoy' in type_inv:
            comprobante = 'cfdi:Comprobante'
            emisor = 'cfdi:Emisor'
            receptor = 'cfdi:Receptor'
            concepto = 'cfdi:Conceptos'
        else:   
            comprobante = 'cfdi:Comprobante'
            emisor = 'cfdi:Emisor'
            receptor = 'cfdi:Receptor'
            concepto = 'cfdi:Conceptos'

        data_dict = self._get_facturae_invoice_dict_data()[0]
        doc_xml = self.dict2xml(
                {comprobante: data_dict.get(comprobante)}
                # {'comprobante': data_dict.get(comprobante)}
            )
        invoice_number = "sn"
        (fileno_xml, fname_xml) = tempfile.mkstemp(
            '.xml', 'odoo_' + (invoice_number or '') + '__facturae__')
        fname_txt = fname_xml + '.txt'
        f = open(fname_xml, 'w')
        doc_xml.writexml(
            f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')
        f.close()
        os.close(fileno_xml)

        (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'odoo_' + (
            invoice_number or '') + '__facturae_txt_md5__')
        os.close(fileno_sign)


        context.update({
            'fname_xml': fname_xml,
            'fname_txt': fname_txt,
            'fname_sign': fname_sign,
        })

        
        context.update(self._get_file_globals())
        fname_txt, txt_str = self.with_context(context)._xml2cad_orig()
        data_dict['cadena_original'] = txt_str
        context.update({
            'cadena_original': txt_str
        })
        if not txt_str:
            raise UserError(
                _("Error in Original String!\n"
                  "Can't get the string original of the voucher.\n"
                  "Ckeck your configuration.")
            )
        # TODO: Is this validation needed?
        if not data_dict[comprobante].get('Folio', ''):
            raise ValidationError(
                _("Error in Folio!\n"                
                  "Can't get the folio of the voucher.\n"
                  "Before generating the XML, click on the button, "
                  "generate invoice.\nCkeck your configuration.\n")
            )

        context.update({'fecha': data_dict[comprobante]['Fecha']})
        sign_str = self.with_context(context)._get_sello()
        if not sign_str:
            raise ValidationError(
                _("Error in Stamp !\n"                
                  "Can't generate the stamp of the voucher.\n"
                  "Ckeck your configuration.")
            )

        nodeComprobante = doc_xml.getElementsByTagName(comprobante)[0]
        nodeComprobante.setAttribute("Sello", sign_str)
        data_dict[comprobante]['Sello'] = sign_str

        noCertificado = self._get_noCertificado(context['fname_cer'])
        if not noCertificado:
            raise ValidationError(
                _("Error in No. Certificate !\n"                
                  "Can't get the Certificate Number of the voucher.\n"
                  "Ckeck your configuration.")
            )
        nodeComprobante.setAttribute("NoCertificado", noCertificado)
        data_dict[comprobante]['NoCertificado'] = noCertificado

        cert_str = self._get_certificate_str(context['fname_cer'])
        if not cert_str:
            raise ValidationError(
                _("Error in Certificate!\n"                
                  "Can't get the Certificate Number of the voucher.\n"
                  "Ckeck your configuration.")
            )
        cert_str = cert_str.replace(' ', '').replace('\n', '')
        nodeComprobante.setAttribute("Certificado", cert_str)
        data_dict[comprobante]['Certificado'] = cert_str

        x = doc_xml.documentElement
        nodeReceptor = doc_xml.getElementsByTagName(receptor)[0]
        nodeConcepto = doc_xml.getElementsByTagName(concepto)[0]
        x.insertBefore(nodeReceptor, nodeConcepto)
        self.write_cfd_data(data_dict)
        
        if context.get('type_data') == 'dict':
            return data_dict
        if context.get('type_data') == 'xml_obj':
            return doc_xml
        data_xml = doc_xml.toxml('UTF-8')
        data_xml = codecs.BOM_UTF8 + data_xml

        fname_xml = (data_dict[comprobante][emisor]['Rfc'] or '') + '_' + (
            data_dict[comprobante].get('Serie', '') or '') + '_' + (
            data_dict[comprobante].get('Folio', '') or '') + '.xml'
        #data_xml = data_xml.replace(
        #    '<?xml version="1.0" encoding="UTF-8"?>',
        #    '<?xml version="1.0" encoding="UTF-8"?>\n')
        return fname_xml, data_xml
