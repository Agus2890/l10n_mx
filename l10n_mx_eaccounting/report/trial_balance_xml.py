# -*- encoding: utf-8 -*-
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Authors: Openpyme (<http://openpyme.mx>)
#
#
#    Coded by: Salvador Martínez (chavamm.83@gmail.com)
#              Miguel Angel Villafuerte Ojeda (mikeshot@gmail.com)
#              Luis Felipe Lores Caignet (luisfqba@gmail.com)
#              Agustín Cruz Lozano (agustin.cruz@openpyme.mx)
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


from odoo import models, fields, api
import xml.etree.ElementTree as ET
#from .report_to_file import Compres
from odoo.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)
####
import os
import tempfile
import zipfile
from datetime import datetime
class TrialBalanceXML(models.TransientModel):
    _inherit = 'report_trial_balance'


    @api.multi
    def print_report_xml_zip(self, report_type):
        self.ensure_one()
        ctx=dict(self.env.context)
        file_name="Balanza_"+str(self.company_id.partner_id.vat_split)
        file=self.with_context(ctx)._get_balance_xml()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            with zipfile.ZipFile(tmp, mode='w') as archive:
                archive.write(file, arcname=file_name+".xml")
                output = tmp.name
        #try:
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?data='+str(output)+'&filename='+file_name+'.zip',
            'target': 'self'}
        #finally:
        #    return True 
            #os.remove(output)

    @api.multi
    def _get_balance_xml(self):
        self.ensure_one()
        date = datetime.strptime(self.date_to, "%Y-%m-%d")
        Etree = ET.ElementTree()
        balanza = ET.Element('BCE:Balanza')
        #namespace   
        balanza.set("xsi:schemaLocation", 
                    "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion/BalanzaComprobacion_1_3.xsd")
        balanza.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        balanza.set("xmlns:BCE", "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion")
        balanza.set('Version', '1.3')
        balanza.set('RFC', self.company_id.partner_id.vat_split)
        balanza.set('Mes', str(date.month).rjust(2, '0'))
        balanza.set('Anio', str(date.year))
        balanza.set('TipoEnvio',self.env.context.get('id_act').type_send)
        Etree._setroot(balanza)
        for account in self.account_ids.filtered(lambda a: not a.hide_line):        
            cuenta = ET.SubElement(balanza, 'BCE:Ctas')
            cuenta.set("NumCta",str(account.code))
            cuenta.set("SaldoIni",str(account.initial_balance))
            cuenta.set("Debe",str(account.debit))
            cuenta.set("Haber",str(account.credit))
            cuenta.set("SaldoFin",str(account.final_balance))
        with tempfile.NamedTemporaryFile(delete=False) as report:
            Etree.write(report.name, encoding='UTF-8')
            fname = report.name
        return fname