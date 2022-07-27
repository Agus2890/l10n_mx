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

import re
from odoo import models,api
from odoo import fields
import xml.etree.cElementTree as ET
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class FoliosAuxiliaryWizardXml(models.TransientModel):
    _name = "folios.auxiliary.wizard.xml"

    date_range_id= fields.Many2one(
            'date.range', 'Fiscal Year',
            help=_('Select period for your chart report'))
    date_from=fields.Date(string="Fecha Inicio",required=True)
    date_to=fields.Date(string="Fecha Final",required=True)
    target_move = fields.Selection(
            [('posted', 'All Posted Entries'),
             ('all', 'All Entries'), ],
            'Target Moves', required=True,default ='posted'
        )
    type_request = fields.Selection(
            [('AF', 'Acto de Fiscalizacion'),
             ('FC', 'Fiscalización Compulsa'),
             ('DE', 'Devolucion'),
             ('CO', 'Compensacion')],
            'Type of request', required=True
        )
    order_num =fields.Char('Order number', size=13)
    pro_num = fields.Char('Procedure number', size=10)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self:self.env.user.company_id.id,required=True)


    @api.multi
    def generate_report_folios(self, data):
        from datetime import datetime
        time_period = datetime.strptime(self.date_from, "%Y-%m-%d")

        context = self.env.context
        import tempfile
        Etree = ET.ElementTree()

        polizas = ET.Element('RepAux:RepAuxFol')
        polizas.set("xsi:schemaLocation",
                    "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarFolios http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarFolios/AuxiliarFolios_1_2.xsd")
        polizas.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        polizas.set("xmlns:RepAux","http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarFolios")

        polizas.set('Version', '1.2')
        polizas.set('RFC', 'vat_split')
        polizas.set('Mes', str(time_period.month).rjust(2, '0'))
        polizas.set('Anio', str(time_period.year))
        polizas.set('TipoSolicitud', self.type_request)
        if self.order_num:
            polizas.set('NumOrden', self.order_num)
        if self.pro_num:
            polizas.set('NumTramite', self.pro_num)
        Etree._setroot(polizas)
        sql_select = """
        SELECT inv.id as factura,am.name,am.date
        from account_invoice as inv
        inner join account_move am on (inv.move_id=am.id)"""
        sql_where = """
        WHERE am.date >=  %(date)s
        AND am.date <=  %(date_to)s
        AND inv.cfdi_folio_fiscal is not null
        AND inv.type='out_invoice'"""
        search_params = {
            'date': self.date_from,
            'date_to': self.date_to,
        }
        sql_joins = ''
        sql_orderby = 'ORDER BY inv.move_id'
        if self.target_move == 'posted':
            sql_where += """ AND am.state = %(target_move)s"""
            search_params.update({'target_move': self.target_move})
        query_sql = ' '.join((sql_select, sql_joins, sql_where, sql_orderby))
        self.env.cr.execute(query_sql, search_params)
        lines = self.env.cr.dictfetchall()
        for line in lines:
            invoice_id=self.env['account.invoice'].browse(line.get('factura'))
            DetAuxFol = ET.SubElement(polizas, 'RepAux:DetAuxFol')
            DetAuxFol.set("NumUnIdenPol", str(line.get('name')))
            DetAuxFol.set("Fecha", str(invoice_id.move_id.date ))
            #####
            ComprNal=ET.SubElement(DetAuxFol,'RepAux:ComprNal')
            ComprNal.set("UUID_CFDI", str(invoice_id.cfdi_folio_fiscal ))
            ComprNal.set("RFC", str(invoice_id.partner_id.vat_split ))
            ComprNal.set("MontoTotal", str(invoice_id.amount_total ))
            ComprNal.set("Moneda", str(invoice_id.currency_id.name ))
            ComprNal.set("TipCamb", str(invoice_id.rate ))

    
        with tempfile.NamedTemporaryFile(delete=False) as report:
            Etree.write(report.name, encoding='UTF-8')
            self.fname = report.name
        return report.name

    @api.multi
    def print_report(self):

        data= {

            "target_move": self.target_move,
            'type_request': self.type_request,
            'order_num': self.order_num,
            'pro_num':self.pro_num,
            'date_from': self.date_from,
            'date_to':self.date_to,
        }
        file=self.generate_report_folios(data)
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?data='+str(file)+'&filename=AuxiliarFolios_'+str(self.company_id.partner_id.vat_split)+'.xml',
            'target': 'self'}