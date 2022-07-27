# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2008 MKI - http://www.mikrointeracciones.com.mx/
#    All Rights Reserved.
#    ihttp://www.mikrointeracciones.com.mx/web/
############################################################################
#    Coded by: Richard (ricardo.gutierrez@mikrointeracciones.com.mx)
############################################################################
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

from odoo import api, models, fields
from odoo.tools.translate import _
from odoo.osv import expression


class AccountAccountSatGroup(models.Model):
    _name = 'account.account.sat_group'


    code = fields.Char(string='Code', size=50)
    name =  fields.Char(string='Name', size=225)
    level = fields.Integer(string='Level')
    sat_group_parent_id = fields.Many2one(
        'account.account.sat_group', string=_('SAT Group Parent')
    )

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
    #         if operator in expression.NEGATIVE_TERM_OPERATORS:
    #             domain = ['&', '!'] + domain[1:]
    #     sat_code = self.search(domain + args, limit=limit)
    #     return sat_code.name_get()

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
        for code_sat in self:
            name = code_sat.code + ' ' + code_sat.name
            result.append((code_sat.id, name))
        return result




# class AccountAccountTemplate(models.Model):
#     _inherit = 'account.account.template'


#     def _get_account_vals(self, company, account_template, code_acc, tax_template_ref):
#         """ This method generates a dictionnary of all the values for the account that will be created.
#         """
#         self.ensure_one()
#         tax_ids = []
#         for tax in account_template.tax_ids:
#             tax_ids.append(tax_template_ref[tax.id])
#         val = {
#                 'name': account_template.name,
#                 'currency_id': account_template.currency_id and account_template.currency_id.id or False,
#                 'code': code_acc,
#                 'user_type_id': account_template.user_type_id and account_template.user_type_id.id or False,
#                 'reconcile': account_template.reconcile,
#                 'note': account_template.note,
#                 'tax_ids': [(6, 0, tax_ids)],
#                 'company_id': company.id,
#                 'tag_ids': [(6, 0, [t.id for t in account_template.tag_ids])],
#                 'sat_group_id': account_template.sat_group_id.id,
#             }
#         return val

#     @api.multi
#     def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
#         """ This method for generating accounts from templates.

#             :param tax_template_ref: Taxes templates reference for write taxes_id in account_account.
#             :param acc_template_ref: dictionary with the mappping between the account templates and the real accounts.
#             :param code_digits: number of digits got from wizard.multi.charts.accounts, this is use for account code.
#             :param company_id: company_id selected from wizard.multi.charts.accounts.
#             :returns: return acc_template_ref for reference purpose.
#             :rtype: dict
#         """
#         self.ensure_one()
#         account_tmpl_obj = self.env['account.account.template']
#         acc_template = account_tmpl_obj.search([('nocreate', '!=', True), ('chart_template_id', '=', self.id)], order='id')
#         for account_template in acc_template:
#             code_main = account_template.code and len(account_template.code) or 0
#             code_acc = account_template.code or ''
#             if code_main > 0 and code_main <= code_digits:
#                 code_acc = str(code_acc) + (str('0'*(code_digits-code_main)))
#             vals = self._get_account_vals(company, account_template, code_acc, tax_template_ref)
#             new_account = self.create_record_with_xmlid(company, account_template, 'account.account', vals)
#             acc_template_ref[account_template.id] = new_account
#         return acc_template_ref

class AccountAccount(models.Model):
    _inherit = 'account.account'
     
    nature = fields.Selection(
        [('D', 'Deudora'),
         ('A', 'Acreedora')
         ],
        string='Naturaleza',
        help=_('Express the account nature (Debitor or Creditor)')
    )
    sat_group_id = fields.Many2one(
        'account.account.sat_group', string='SAT Group',
        ondelete='set null',
        help=_('Used for express the group code according to SAT catalog')
    )

    def _check_account(self):
        # Validates that view type account must have a SAT group defined
        # except for the account with code "0"
        for account in self:
            if not account.sat_group_id and \
                account.user_type_id == "view" and \
                    account.code != "0":
                return False
        return True
    
    def _check_account_nature(self):
        """
        This function checks that is not created an account without a nature
        if have added a SAT group
        """
        for account in self:
            if account.sat_group_id and not account.nature:
               return False
            return True 

    _constraints = [
        (_check_account, 'Not defined a SAT group for the account!\n'
            'A view type account must have a SAT group defined!',
            ['sat_group_id']),
        (_check_account_nature, 'Not defined a Nature Account!\n'
            'We cannot create an account with SAT group and without nature',
            ['sat_group_id']),
    ]


# class AccountAccountTemplate(models.Model):
#     _inherit = 'account.account.template'
    
    
#     nature = fields.Selection(
#         [('D', 'Deudora'),
#          ('A', 'Acreedora')
#          ],
#         string='Naturaleza',
#         help='Express the account nature (Debitor or Creditor)'
#     )
#     sat_group_id = fields.Many2one(
#         'account.account.sat_group', string='SAT Group',
#         ondelete='set null',
#         help='Used for express the group code according to SAT catalog'
#     )

#     def _check_account(self):
#         # Validates that view type account must have a SAT group defined
#         # except for the account with code "0"
#         for account in self:
#             if not account.sat_group_id and \
#                 account.type == "view" and \
#                     account.code != "0":
#                 return False
#         return True

#     _constraints = [
#         (_check_account, 'Not defined a SAT group for the account!\n'
#             'A view type account must have a SAT group defined!',
#             ['sat_group_id']),
#     ]
