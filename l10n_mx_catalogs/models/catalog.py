# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
import os
from odoo import tools, netsvc
import xlrd
import xlwt
# try:
#     import excelrd as xlrd
# except ImportError:
#     raise Warning("Warning",'Install xlrd in server-->sudo apt-get install python-xlrd ')
# try:
#     import xlwt
# except ImportError:
#     raise Warning("Warning",'Install xlrd in server')

import logging
_logger = logging.getLogger(__name__)


class KeyProductSat(models.Model):
    _name = 'key.product.sat'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code_sat', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()

    @api.depends('name', 'code_sat')
    def name_get(self):
        result = []
        for account in self:
            name = account.code_sat + ' ' + account.name
            result.append((account.id, name))
        return result


    @api.model
    def import_cat_prod_xls(self):
        cat_prod_obj  = self.env['key.product.sat']
        rows=cat_prod_obj.search_count([])
        if rows<=0:
            FILE=False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_catalogs', 'data')
                ):
                    FILE=my_path and os.path.join(my_path, 'l10n_mx_catalogs', 'data','l10n_mx_cat_prod.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_idlot=False
            for rx in range(sh.nrows):
                lines_inv={
                    'code_sat': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value
                }
                cat_prod_obj.create(lines_inv)
        return True

    code_sat=fields.Char(string='Codigo',size=30)
    name=fields.Char(string='Descripcion',size=128)


class key_unit_sat(models.Model):
    _name = 'key.unit.sat'
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code_sat', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()

    @api.depends('name', 'code_sat')
    def name_get(self):
        result = []
        for account in self:
            name = account.code_sat + ' ' + account.name
            result.append((account.id, name))
        return result

    @api.model
    def import_cat_unit_xls(self):
        cat_unit_obj  = self.env['key.unit.sat']
        rows=cat_unit_obj.search_count([])
        if rows<=0:
            FILE=False
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(
                    os.path.join(my_path, 'l10n_mx_catalogs', 'data')
                ):
                    FILE=my_path and os.path.join(my_path, 'l10n_mx_catalogs', 'data','l10n_mx_cat_unit.xlsx') or ''
            book = xlrd.open_workbook(FILE)
            sh = book.sheet_by_index(0)
            new_idlot=False
            for rx in range(sh.nrows):
                lines_inv={
                    'code_sat': str(sh.row(rx)[0].value).replace(".0",""),
                    'name': sh.row(rx)[1].value,
                    'description': sh.row(rx)[2].value,
                    # 'location_id': sh.row(rx)[3].value
                }
                cat_unit_obj.create(lines_inv)
        return True

    code_sat=fields.Char(string='Codigo',size=30)
    name=fields.Char(string='Nombre',size=128)
    description=fields.Char(string='Descripcion',size=128)
    note=fields.Text(string='Notas')


class uso_cfdi_sat(models.Model):
    _name = 'uso.cfdi'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()

    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for account in self:
            name = account.code + ' ' + account.name
            result.append((account.id, name))
        return result

    name=fields.Char(string='Descripcion',size=128)
    code=fields.Char(string='Codigo',size=30)
