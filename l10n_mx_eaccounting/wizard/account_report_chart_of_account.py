# -*- encoding: utf-8 -*-
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
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

from odoo.tools.translate import _
from odoo import fields,models,api
from odoo.exceptions import ValidationError
#from . import ReportToFile
from datetime import datetime
import xml.etree.cElementTree as ET
import tempfile
import zipfile
import base64
class ChartOfAccountsReport(models.TransientModel):
    _name = 'account.print.chart.accounts.report'

    chart_account_id = fields.Many2one('account.account',string='Chart of Accounts')
    date=fields.Date(string="Date",required=True,default=fields.Date.today())
    company_id = fields.Many2one('res.company', 'Company', default=lambda self:self.env.user.company_id.id,required=True)

    def compress(file_temp, file_name, fext='txt', comp='zip'):
        new_name = '.'.join([file_name, fext])
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            with zipfile.ZipFile(tmp, mode='w') as archive:
                archive.write(file_temp, arcname=new_name)
            output = tmp.name
        return output
        
    @api.multi
    def print_report(self):
        date = datetime.strptime(self.date, "%Y-%m-%d")
        file_name="Catalogo_"+str(self.company_id.partner_id.vat_split)
        report_xml=False
        Etree = ET.ElementTree()
        catalogo = ET.Element('catalogocuentas:Catalogo')
        #namespace        
        catalogo.set("xsi:schemaLocation", 
                    "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas/CatalogoCuentas_1_3.xsd")
        catalogo.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        catalogo.set("xmlns:catalogocuentas", "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas")
        catalogo.set("Version", "1.3")
        catalogo.set("RFC",str(self.company_id.partner_id.vat_split))
        catalogo.set("Mes",str(date.month).rjust(2, '0'))
        catalogo.set("Anio",str(date.year))
        Etree._setroot(catalogo)
        account_ids=self._get_lst_account()
        for acc in account_ids:
            if acc.sat_group_id:
                cuenta = ET.SubElement(catalogo, 'catalogocuentas:Ctas')
                # Codigo agrupador poner el Codigo no el Nombre
                cuenta.set("CodAgrup", str(acc.sat_group_id.code))
                cuenta.set("NumCta", acc.code)
                cuenta.set("Desc", acc.name)
                if acc.parent_id and acc.sat_group_id.level > 1:
                    cuenta.set("SubCtaDe", acc.parent_id.code)
                cuenta.set("Nivel", str(acc.sat_group_id.level))
                cuenta.set("Natur", acc.nature)
        with tempfile.NamedTemporaryFile(delete=False) as report:
            Etree.write(report.name, encoding='UTF-8')
            report_xml= report.name
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
           with zipfile.ZipFile(tmp, mode='w') as archive:
               archive.write(report_xml, arcname=file_name+'.xml')
           output = tmp.name
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?data='+str(output)+'&filename='+file_name+'.zip',
            'target': 'self'}

    @api.multi
    def _get_lst_account(self):
        return self.env['account.account'].search([('internal_type','!=','view'),('company_id','=',self.company_id.id)])