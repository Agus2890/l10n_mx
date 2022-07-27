# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
import time
from datetime import datetime,date,timedelta
import logging
_logger = logging.getLogger(__name__)

class res_company(models.Model):
    _inherit = 'res.company'

    # @api.constrains('folio_lines')   
    # def _validate_active_timbres(self):
    #     if self.folio_id:
    #         now = datetime.now().strftime('%Y-%m-%d')
    #         account=[r for r in self.folio_lines if r.check==True]
    #         if len(account)>=2:
    #             raise except_orm("Warning","Solo puede tener una linea de folios activos")
    # _sql_constraints = [('folio_lines','active','solo un activo')]

    @api.depends('folio_lines')
    def _total_folios(self):
        for folio in self.folio_lines:
            if folio.check==True:
                self.datein=folio.datein
                self.datefin=folio.datefin
                self.qty=folio.qty
                self.consumidos=folio.consumidos
                self.amount=folio.amount
                self.folio_id=folio.id
                break

    @api.multi
    def check_folios_active(self):
        folio=0
        now = datetime.now().strftime('%Y-%m-%d')
        if self.folio_id:
            if self.folio_id.datefin<now:
                raise except_orm("Warning",str("Revice la Fecha vencimineto  de folios"))
            folio=self.folio_id.amount
        return folio

    folio_lines=fields.One2many("res.company.folios","company_id",string="Lineas")
    datein=fields.Date(compute="_total_folios",string="Fecha Compra")
    datefin=fields.Date(compute="_total_folios",string="Fecha Vencimiento")
    qty=fields.Float(compute="_total_folios",string="Cantidad Folios")
    consumidos=fields.Float(compute="_total_folios",string="Folios Consumidos")
    amount=fields.Float(compute="_total_folios",string="Folios Restantes")
    folio_id=fields.Many2one("res.company.folios",compute="_total_folios",string="Folio",reandoly=True)

class res_company_folios(models.Model):
    _name = 'res.company.folios'

    @api.depends('qty')
    def _tiimbres_consumidos(self):
        journal=self.env['account.journal'].search([('type_cfdi','=',self.pac_id)])
        accout=self.env['account.invoice'].search_count([('journal_id','=',[r.id for r in journal]),
            ('type','in',('out_invoice','out_refund')),('state','!=','draft'),
            ('cfdi_folio_fiscal','!=',False),('date_invoice','>=',self.datein),
            ('date_invoice','<=',self.datefin),('company_id','=',self.company_id.id)])
        nomina=0
        if self.datein: 
            date1=datetime.strptime(self.datein+" "+"00:00:00","%Y-%m-%d %H:%M:%S")
        if self.datefin:
            date2=datetime.strptime(self.datefin+" "+"23:59:00","%Y-%m-%d %H:%M:%S")
            nomina=self.env['hr.payslip'].search_count([('journal_id','=',[r.id for r in journal]),
                ('state','!=','draft'),('cfdi_folio_fiscal','!=',False),('date_payroll','>=',date1.strftime('%Y-%m-%d %H:%M:%S')),
                ('date_payroll','<=',date2.strftime('%Y-%m-%d %H:%M:%S')),('company_id','=',self.company_id.id)])
        self.consumidos=accout+nomina
        self.amount=self.qty-accout+nomina

    company_id=fields.Many2one("res.company",string="Compania")
    pac_id=fields.Selection([],string="Pac",required=True)
    datein=fields.Date("Fecha Compra",required=True)
    datefin=fields.Date("Fecha Vencimiento",required=True)
    qty=fields.Float(string="Cantidad Folios",required=True)
    consumidos=fields.Float(compute="_tiimbres_consumidos",string="Folios Consumidos")
    amount=fields.Float(compute="_tiimbres_consumidos",string="Folios Restantes")
    check=fields.Boolean("Activo")

