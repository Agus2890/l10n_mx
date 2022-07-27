# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class AccountFiscalPosition(models.Model):
    _inherit ='account.fiscal.position'
    
    clave = fields.Char(string='Clave Sat', size=30)
    description = fields.Text('Descripcion')    