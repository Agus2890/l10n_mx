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

import xml.etree.cElementTree as ET
from odoo import fields,models,api,_
#from .report_to_file import ReportToFile
# from ernesto.account_chart_report.report.chart_of_accounts import AccountChar
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime


class AccountChartXml(models.AbstractModel):
    _name = 'report.l10n_mx_eaccounting.account_chart_xml'

    @api.model
    def get_report_values(self, docids, data=None):
        #if not data.get('form'):
        #    raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            #'doc_ids': docs.ids,
            #'lines': self.get_lines(data.get('form')),
            #'get_taxes': self.get_taxes(),
            #'get_taxes_ret': self._get_taxes_ret,
            #'get_text_promissory': self._get_text_promissory,
            #'get_emitter_data': self._get_emitter_data,
            #'get_partner_data': self._get_partner_data,
            'get_lst_account': self.get_lst_account()
            #'legend': self._get_legend,
        }

    @api.model
    def get_lst_account(self):
        return self