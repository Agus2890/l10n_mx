# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class rescountry(models.Model):
    _inherit = "res.country"

    code = fields.Char(string='Código de país',size=5)


