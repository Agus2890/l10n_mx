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


class AccountAuxiliaryWizardXml(models.TransientModel):
    """
    Almost copy exactly the general_ledger_wizard class form Webkit Reports
    because if try to inherit the class openerp could find all the fields
    needed for render the view
    """
    _inherit = "account.common.account.report"
    _name = "account.auxiliary.wizard.xml"

#     def _get_account_ids(self,context=None):
#         res = False
#         if context.get('active_model', False) == 'account.account' and context.get('active_ids', False):
#             res = context['active_ids']
#         return res

#     fiscalyear_id = fields.Many2one(
#             'account.fiscalyear', 'Period',
#             help=_('Select period for your chart report'),
# #             required=True
#         )
#     period_id = fields.Many2one('account.period', 'Period',help=_('Select period for your chart report'))
    date_range_id= fields.Many2one(
                'date.range', 'Fiscal Year',
                help=_('Select period for your chart report'))
    date_from=fields.Date(string="Fecha Inicio",required=True)
    date_to=fields.Date(string="Fecha Final",required=True)

    type_request = fields.Selection(
            [('AF', 'Control act'),
             ('FC', 'Certifying audit'),
             ('DE', 'Return'),
             ('CO', 'Write off')],
            'Type of request', required=True
        )
    order_num = fields.Char('Order number', size=13)
    pro_num = fields.Char('Procedure number', size=10)
    account_ids = fields.Many2many(
            'account.account', string='Filter on accounts',
            help="""Only selected accounts will be printed. Leave empty to
                    print all accounts."""
            )


    def _check_fiscalyear_old(self):
        obj = self.read(['fiscalyear_id', 'filter'])
        if not obj['fiscalyear_id'] and obj['filter'] == 'filter_no':
            return False
        return True

    def _check_order_num_old(self,context=None):
        res = self.read()[0]
        if res["order_num"] and res['type_request'] in ['AF', 'FC']:
            patron_order_num = re.compile('[A-Z]{3}[0-6][0-9][0-9]{5}(/)[0-9]{2}')
            match_order_num = patron_order_num.match(res["order_num"])
            if not match_order_num:
                return False
        return True

    def _check_pro_num_old(self, context=None):
        res = self.read()[0]
        if res["pro_num"] and res['type_request'] in ['DE', 'CO']:
            patron_pro_num = re.compile('[0-9]{10}')
            match_pro_num = patron_pro_num.match(res["pro_num"])
            if not match_pro_num:
                return False
        return True

    def _check_accounts_old(self, context=None):
        """
        Checks that the user selects an account to be included on the report
        """
        res = self.read()[0]
        if not res['account_ids']:
            return False
        return True

#     _constraints = [
#         (_check_fiscalyear,
#          'When no Fiscal year is selected, you must choose to filter by \
#          periods or by date.', ['filter']),
#         (_check_order_num,
#          'Order number not valid.\nVerify that the pattern is correct!',
#          ['order_num']),
#         (_check_pro_num,
#          'Procedure number not valid.\nVerify that the pattern is correct!',
#          ['pro_num']),
#         (_check_accounts,
#          'You must select an account to include in report!',
#          ['account_ids']),
#     ]

    def onchange_fiscalyear_id_old(self, fiscalyear_id=False):
        """
        Update the period in the wizard based on the fiscal year
        """
        res = {}
        res['value'] = {}
        if fiscalyear_id:
            period = False
            self.env.cr.execute('''
                SELECT * FROM (
                    SELECT p.id
                    FROM account_period p
                    LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                    WHERE f.id = %s AND p.special = False
                    ORDER BY p.date_start ASC
                    LIMIT 1) AS period_start''' % fiscalyear_id)
            periods = [i[0] for i in self.env.cr.fetchall()]
            if periods and len(periods) > 0:
                period = periods[0]
            res['value'] = {'period_id': period}
        return res

    def pre_print_report_olds(self,data):
        data = super(AccountAuxiliaryWizardXml, self).pre_print_report(data)
        # will be used to attach the report on the main account
#         data['ids'] = [data['form']['chart_account_id']]
        vals = self.read(['account_ids'])[0]
        data['form'].update(vals)
        return data

    def validate_vat_old(self):
        # Validates that the company has VAT configured properly
        company_id = self.env['res.company']._company_default_get(object='account.print.chart.accounts.report')
        company = self.env['res.company'].browse(company_id).id
        vat_split = company.partner_id

        if not vat_split:
            raise ValidationError(
                _('Error'),
                _('Not found information for VAT of Company.\n'
                  'Verify that the configuration of VAT is correct!')
            )

        return

    def build_report_name_old(self,data):
        """
        Builds the name of report
        """
        from datetime import datetime
        res = self.read()[0]
#         period_id = res['period_id'][0]
#         period_date = datetime.strptime(
#             self.env['account.period'].browse(period_id).date_stop, "%Y-%m-%d")
        company_id = self.env['res.company']._company_default_get(object='account.print.chart.accounts.report')
        company = self.env['res.company'].browse(company_id).id
        vat_split = company.partner_id

        report_name_sat = ''.join([
#             vat_split,
#             str(period_date.year),
#             str(period_date.month).rjust(2, '0'),
            'XC']
        )
        return report_name_sat

#     def generate_xml_report(self,data, context=None):
#         self.validate_vat()
# 
#         res = self.browse()
#         report_name = self.build_report_name(data)
#         data['form'] = {
# #             'chart_account_id': res.chart_account_id.id,
# #             'fiscalyear_id': res.fiscalyear_id.id,
# #             'period_id': res.period_id.id,
# #             'date': res.period_id.date_start,
#             'target_move': res.target_move,
#             'type_request': res.type_request,
# #             'order_num': res.order_num,
# #             'pro_num': res.pro_num,
#         }
#         data = self.pre_print_report(data)
#         return {
#             'type': 'ir.actions.report.xml',
#             'report_name': 'account.auxiliar_ledger_xml',
#             'datas': data,
#             'name': report_name,
#             'context': {
#                 'FileExt': 'xml',
#                 'compress': True,
#                 'FileName': report_name
#             }
#         }

    def generate_report__old(self ,data =None):
        """
        Function that generate the XML structure for report
        """
        # Create main journal entries node
        from datetime import datetime
#         time_period = datetime.strptime(
#             self.datas['form']['date'], "%Y-%m-%d"
#         )
        aux = ET.Element('AuxiliarCtas:AuxiliarCtas')
        #namespace        
        aux.set("xsi:schemaLocation", 
                "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas/AuxiliarCtas_1_1.xsd")
        aux.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        aux.set("xmlns:AuxiliarCtas", "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas")
        
        aux.set('Version', '1.1')
#         aux.set('RFC', self.localcontext['company'].partner_id.vat_split)
#         aux.set('Mes', str(time_period.month).rjust(2, '0'))
#         aux.set('Anio', str(time_period.year))
#         aux.set('TipoSolicitud', self.datas["form"]["type_request"])
#         if self.datas["form"]["order_num"]:
#             aux.set('NumOrden', self.datas["form"]["order_num"])
#         if self.datas["form"]["pro_num"]:
#             aux.set('NumTramite', self.datas["form"]["pro_num"])
        # Start processing data
        for account in self.account_ids:
            if account:
                cumul_balance = 0
                accNode = ET.SubElement(aux, 'AuxiliarCtas:Cuenta')
                accNode.set('NumCta', account.code)
                accNode.set('DesCta', account.name)
                accNode.set(
                    'SaldoIni', str(account.init_balance.get('init_balance', 0))
                )
                for line in account:
                    cumul_balance += line.get('balance', 0)
                    label_elements = [line.get('lname', '')]
                    if line.get('invoice_number'):
                        label_elements.append("(%s)" % (line['invoice_number'],))
                    label = ' '.join(label_elements)
                    detail = ET.SubElement(accNode, 'AuxiliarCtas:DetalleAux')
                    detail.set('Fecha', line.get('ldate'))
                    detail.set('NumUnIdenPol', line.get('move_name'))
                    detail.set('Concepto', label)
                    detail.set('Debe', str(line.get('debit', 0.0)))
                    detail.set('Haber', str(line.get('credit', 0.0)))
                accNode.set('SaldoFin', str(cumul_balance))
        Etree = ET.ElementTree(aux)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as report:
            Etree.write(report.name, encoding='UTF-8')
            fname = report.name

        return fname
    

    @api.multi
    def print_report(self):
        return self.env['report'].get_action([],'l10n_mx_eaccounting.general_ledger_mx_report')
    