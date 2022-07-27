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
from odoo import models
from odoo import fields,api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class trial_balance_wizard_xml(models.TransientModel):
    _inherit = 'trial.balance.report.wizard'
    
    type_send=fields.Selection([('N', 'Normal'),('C', 'Complementaria')],string='Type Send', required=True,default="N")

    @api.multi
    def button_export_xml(self):
        self.ensure_one()
        report_type = 'xml'
        return self._export_xml(report_type)


    def _export_xml(self, report_type):
        model = self.env['report_trial_balance']
        report = model.create(self._prepare_report_trial_balance())
        report.compute_data_for_report()
        return report.with_context({'id_act':self}).print_report_xml_zip(report_type)