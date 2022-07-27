# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
# from odoo.addons import decimal_precision as dp


# class AccountInvoice(models.Model):
#     _inherit = "account.invoice"

#     @api.one
#     @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
#                  'currency_id', 'company_id', 'date_invoice', 'type')
#     def _compute_amount(self):
#         round_curr = self.currency_id.round
#         self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
#         self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids if line.amount >= 0 and not line.tax_id.tax_category_id.name == 'IEPS' )
#         self.amount_tax_ret = sum(round_curr(line.amount) for line in self.tax_line_ids if line.amount <= 0 and line.tax_id.tax_category_id.name == 'IVA-RET' )
#         self.amount_tax_ieps = sum(round_curr(line.amount) for line in self.tax_line_ids if line.tax_id.tax_category_id.name == 'IEPS')
#         self.amount_tax_local = sum(round_curr(line.amount) for line in self.tax_line_ids if line.amount <= 0 and line.tax_id.tax_category_id.name == 'LOCAL')
#         self.amount_total = self.amount_untaxed + self.amount_tax + self.amount_tax_ret + self.amount_tax_ieps + self.amount_tax_local
#         amount_total_company_signed = self.amount_total
#         amount_untaxed_signed = self.amount_untaxed
#         if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
#             currency_id = self.currency_id
#             amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
#             amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
#         sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
#         self.amount_total_company_signed = amount_total_company_signed * sign
#         self.amount_total_signed = self.amount_total * sign
#         self.amount_untaxed_signed = amount_untaxed_signed * sign

#     amount_tax = fields.Monetary(string='Tax',
#         store=True, readonly=True, compute='_compute_amount')
#     amount_tax_ret = fields.Monetary(string='Taxe withheld',
#         store=True, readonly=True, compute='_compute_amount')
#     amount_tax_ieps = fields.Monetary(string='IEPS',
#         store=True, readonly=True, compute='_compute_amount')
#     amount_tax_local = fields.Float(string='Tax local',
#         store=True, readonly=True, compute='_compute_amount')
#     amount_total = fields.Monetary(string='Total',
#         store=True, readonly=True, compute='_compute_amount')


# class AccountInvoiceTax(models.Model):
#     _inherit = "account.invoice.tax"

#     def _get_tax_data(self,field_names=None, arg=False):
#         res = {}
#         for invoice_tax in self:
#             res[invoice_tax.id] = {}
#             tax = 'tax_id' in self and invoice_tax.tax_id or False  # 
#             tax_name = (tax and tax.tax_category_id and \
#                 tax.tax_category_id.code or invoice_tax.name).upper().replace(
#                 '.', '').replace(' ', '').replace('-', '')
#             tax_percent = (
#                 tax and tax.amount * 100.0 or False)
#             tax_percent = tax_percent or (
#                 invoice_tax.amount and invoice_tax.base and \
#                 invoice_tax.amount * 100.0 / abs(invoice_tax.base) or 0.0)
#             if 'IVA' in tax_name:
#                 tax_name = 'IVA'
#                 if not tax and tax_percent > 0:
#                     tax_percent = round(
#                         tax_percent, 0) 
#             elif 'ISR' in tax_name:
#                 tax_name = 'ISR'
#             elif 'IEPS' in tax_name:
#                 tax_name = 'IEPS'
#             res[invoice_tax.id]['name2'] = tax_name
#             res[invoice_tax.id]['tax_percent'] = tax_percent
#         return res

#     name2 = fields.Char(compute='_get_tax_data', method=True, type='char',
#                 size=64, string='Tax Short Name', multi='tax_percent',
#                 store=True, help="Is the code of category of the tax or name \
#                 of tax but in uppers, without '.', '-', ' '")
#     tax_percent = fields.Char(compute='_get_tax_data', method=True, type='float',
#                 string='Tax Percent', multi='tax_percent', store=True,)
