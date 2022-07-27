# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # @api.one
    # @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'currency_id', 'company_id', 'date_invoice')
    # def _compute_amount(self):
    #     self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
    #     self.amount_tax = sum(line.amount for line in self.tax_line)
    #     self.amount_total = self.amount_untaxed + self.amount_tax
    #     self.amount_discount = sum((line.quantity * line.price_unit * line.discount)/100 for line in self.invoice_line)

    # @api.one
    # @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
    #              'currency_id', 'company_id', 'date_invoice', 'type')
    # def _compute_amount(self):
    #     round_curr = self.currency_id.round
    #     self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
    #     self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
    #     self.amount_total = self.amount_untaxed + self.amount_tax
    #     self.amount_discount = sum((line.quantity * line.price_unit * line.discount)/100 for line in self.invoice_line_ids)
    #     amount_total_company_signed = self.amount_total
    #     amount_untaxed_signed = self.amount_untaxed
    #     if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
    #         currency_id = self.currency_id.with_context(date=self.date_invoice)
    #         amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
    #         amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
    #     sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
    #     self.amount_total_company_signed = amount_total_company_signed * sign
    #     self.amount_total_signed = self.amount_total * sign
    #     self.amount_untaxed_signed = amount_untaxed_signed * sign

    # @api.multi
    # def button_reset_taxes(self):
    #     res = super(AccountInvoice, self).button_reset_taxes()
    #     self.get_discount_fixed()
    #     return res

    # @api.onchange('discount', 'invoice_line.discount')
    # def get_discount_fixed(self):
    #     for line in self.invoice_line:
    #         if line.discount:
    #             line.discount_fixed = (line.quantity * line.price_unit) - line.price_subtotal

    # @api.multi
    # def button_compute(self, set_total=False):
    #     res = super(AccountInvoice, self).button_compute()
    #     self.get_discount_fixed()
    #     return res

    @api.multi
    def _get_facturae_invoice_dict_data(self):
        invoice_data_parents = super(AccountInvoice, self).\
        _get_facturae_invoice_dict_data()
        if self.amount_discount:
            invoice = self
            sub_tot = 0
            taxes_lines=[]
            total_discount=0.00;
            for line in invoice.invoice_line_ids:
                sub_tot += line.price_unit * line.quantity

                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'Cantidad'] = line.quantity or '0.0'
                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'Descripcion'] = line.name or ' '
                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'Importe'] = "%.2f" % (line.price_unit * line.quantity or '0.00')
                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'NoIdentificacion'] = line.product_id.default_code or '-'

                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'Unidad'] = line.uos_id and line.uos_id.name or ''

                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'ValorUnitario'] = line.price_unit or '0'

                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'ClaveProdServ'] = line.code_product_sat.code_sat
                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'ClaveUnidad'] = line.product_unit_sat.code_sat

                invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                    list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto'][
                    'Descuento'] = line.discount_fixed
                total_discount+=round(line.discount_fixed,2)
                
                if line.discount_fixed:
                    price_unit = line.price_unit * (1 - (line.discount_fixed*100/(line.quantity * line.price_unit) if (line.quantity * line.price_unit) else 1 ) / 100.0)
                    #price = self.price_unit * (1 - (self.discount_fixed or 0.0) / 100.0)
                else:
                    price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.invoice_line_tax_id.compute_all(price_unit,line.quantity, line.product_id, invoice.partner_id)

                for tx in taxes['taxes']:
                    if not taxes_lines: 
                        tx.update({'base2':taxes['total']})
                        taxes_lines.append(tx)
                    else:
                        dupli=False
                        for li in taxes_lines:
                            if  tx["id"]==li['id']:
                                li['amount']+=tx['amount']
                                dupli=True
                        if not dupli:
                            tx.update({'base2':taxes['total']})
                            taxes_lines.append(tx)

                    tax_id=self.env["account.tax"].browse(tx["id"])

                    invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                        list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto']['cfdi:Impuestos']=[]

                    if tx["amount"] >= 0:
                        # raise UserError("",str(taxes))
                        invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Conceptos'][
                        list(invoice.invoice_line_ids).index(line)]['cfdi:Concepto']['cfdi:Impuestos'].append({'cfdi:Traslados': [{'cfdi:Traslado':dict({
                            'Base': "%.2f" %(  abs(taxes['total'] or 0.01)  ),
                            'Impuesto': tax_id.tax_category_id.code_sat,
                            'TipoFactor': tax_id.tax_category_id.type,
                            'TasaOCuota': "%.6f" %(tax_id.amount),
                            'Importe': round(tx["amount"],2)
                            # 'Importe': format(tx['amount'], '.1f')
                        })}]})
                        _logger.info("Iva line ===================================================: %s" % (format(tx['amount'], '.1f')))
            ttraladado=[]
            ttotal = 0
            for tax_line in taxes_lines:
                tax_id = self.env['account.tax'].browse(tax_line['id'])
                ttotal += tax_line['amount'] 
                ttraladado.append({
                        'Impuesto': tax_id.tax_category_id.code_sat,
                        'TipoFactor': tax_id.tax_category_id.type,
                        'TasaOCuota': "%.6f" % ( tax_id.amount),
                        'Importe': "%.2f" % (tax_line['amount']) 
                        # 'Importe': format(tax_line['amount'], '.1f')
                        })
                _logger.info("Iva traslado line ===============================================: %s, %s, %s %s" % (tax_id.tax_category_id.code_sat, tax_id.tax_category_id.type, tax_id.amount, tax_line['amount']))

            _logger.info("Iva traslado ===================================================: %s" % (ttraladado))
            _logger.info("Iva total ===================================================: %s" % (format(ttotal, '.1f')))

            # list(invoice_data_parents[0]['cfdi:Comprobante']).update({['cfdi:Impuestos']:[]})
            # raise UserError("",str(  invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Impuestos']  ))
            # invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Concepto']['cfdi:Impuestos']=[]
            invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Impuestos']=[]

            invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Impuestos'].append({'cfdi:Traslados': [{'cfdi:Traslado': ttraladado}]})
            invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Impuestos'].append({'TotalImpuestosTrasladados': "%.2f" %(ttotal)})
            # invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Impuestos'].append({'TotalImpuestosTrasladados': format(ttotal, '.1f')})
            

            # invoice_data_parents[0]['cfdi:Comprobante']['motivoDescuento'] = invoice.motive_discount or ''
            
            invoice_data_parents[0]['cfdi:Comprobante']['Descuento'] = total_discount
            invoice_data_parents[0]['cfdi:Comprobante']['SubTotal'] = sub_tot
            # invoice_data_parents[0]['cfdi:Comprobante']['Total'] = round(sub_tot+ttotal-total_discount,2)
        return invoice_data_parents

    # @api.model
    # def invoice_line_move_line_get(self):
    #     res = []
    #     for line in self.invoice_line_ids:
    #         if line.quantity==0:
    #             continue
    #         tax_ids = []
    #         for tax in line.invoice_line_tax_ids:
    #             tax_ids.append((4, tax.id, None))
    #             for child in tax.children_tax_ids:
    #                 if child.type_tax_use != 'none':
    #                     tax_ids.append((4, child.id, None))
    #         analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

    #         move_line_dict = {
    #             'invl_id': line.id,
    #             'type': 'src',
    #             'name': line.name.split('\n')[0][:64],
    #             'price_unit': line.price_unit,
    #             'quantity': line.quantity,
    #             'price': line.price_subtotal,
    #             'account_id': line.account_id.id,
    #             'product_id': line.product_id.id,
    #             'uom_id': line.uom_id.id,
    #             'account_analytic_id': line.account_analytic_id.id,
    #             'tax_ids': tax_ids,
    #             'invoice_id': self.id,
    #             'analytic_tag_ids': analytic_tag_ids
    #         }
    #         res.append(move_line_dict)
    #     return res

    # @api.model
    # def tax_line_move_line_get(self):
    #     res = []
    #     # keep track of taxes already processed
    #     done_taxes = []
    #     # loop the invoice.tax.line in reversal sequence
    #     for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
    #         if tax_line.amount_total:
    #             tax = tax_line.tax_id
    #             if tax.amount_type == "group":
    #                 for child_tax in tax.children_tax_ids:
    #                     done_taxes.append(child_tax.id)
    #             res.append({
    #                 'invoice_tax_line_id': tax_line.id,
    #                 'tax_line_id': tax_line.tax_id.id,
    #                 'type': 'tax',
    #                 'name': tax_line.name,
    #                 'price_unit': tax_line.amount_total,
    #                 'quantity': 1,
    #                 'price': tax_line.amount_total,
    #                 'account_id': tax_line.account_id.id,
    #                 'account_analytic_id': tax_line.account_analytic_id.id,
    #                 'invoice_id': self.id,
    #                 'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
    #             })
    #             done_taxes.append(tax.id)
    #     return res

    @api.multi
    def action_move_create(self):
        res=super(AccountInvoice,self).action_move_create()
        if self.move_id and self.type == 'out_invoice':
            self.move_id.button_cancel()
            for line in self.invoice_line_ids.filtered(lambda r: r.discount_fixed>0):
                line_move = self.move_id.line_ids.filtered(lambda r: r.product_id.id == line.product_id.id)
                factor = line.discount_fixed * self.rate
                amount_base = (line.price_unit * line.quantity) * self.rate
                if line_move and line.product_id.categ_id.property_account_discount_income_categ_id:
                    # line_move.write({'credit': line.price_unit * line.quantity})
                    line_move.write({'credit': amount_base, 'tax_amount': amount_base})
                    discount = {
                            'date_maturity': line_move.date_maturity,
                            'partner_id': line_move.partner_id.id,
                            'name': line_move.name + ' (Descuento)',
                            'date': line_move.date,
                            'debit': factor,
                            'credit': 0,
                            'amount_currency': line.discount_fixed if self.currency_id.id != self.company_id.currency_id.id else False,
                            'account_id': line.product_id.categ_id.property_account_discount_income_categ_id.id,
                            'ref': line_move.ref,
                            'move_id': line_move.move_id.id,
                            'company_id': line_move.company_id.id,
                            'currency_id': line_move.currency_id.id,
                            'invoice_id': line_move.invoice_id.id
                        }
                    self.env['account.move.line'].create(discount)
                    _logger.info("===================================================: %s" % (discount))
            self.move_id.post()
        elif self.move_id and self.type == 'in_invoice': 
            self.move_id.button_cancel()
            for line in self.invoice_line_ids.filtered(lambda r: r.discount_fixed>0):
                line_move = self.move_id.line_ids.filtered(lambda r: r.product_id.id == line.product_id.id)
                factor = line.discount_fixed * self.rate
                amount_base = (line.price_unit * line.quantity) * self.rate
                if line_move and line.product_id.categ_id.property_account_discount_expense_categ_id:
                    line_move.write({'debit': amount_base, 'tax_amount': amount_base})
                    discount={
                            'date_maturity': line_move.date_maturity,
                            'partner_id': line_move.partner_id.id,
                            'name': line_move.name + ' (Descuento)',
                            'date': line_move.date,
                            'debit': 0,
                            'credit': factor,
                            'amount_currency': line.discount_fixed * -1 if self.currency_id.id != self.company_id.currency_id.id else False,
                            'account_id': line.product_id.categ_id.property_account_discount_expense_categ_id.id,
                            'ref': line_move.ref,
                            'move_id': line_move.move_id.id,
                            'company_id': line_move.company_id.id,
                            'currency_id': line_move.currency_id.id,
                            'invoice_id': line_move.invoice_id.id
                        }
                    self.env['account.move.line'].create(discount)
            self.move_id.post()
        return res

    amount_discount = fields.Float(string='Discount', default=0.0, store=True, readonly=True,
        compute='_compute_amount', track_visibility='always')

    @api.multi
    def action_date_assign(self):
        res=super(AccountInvoice,self).action_date_assign()
        if self.journal_id.sign_sat:
            for line in self.invoice_line_ids:
                if line.discount:
                    if not line.product_id.categ_id.property_account_discount_income_categ_id:
                        raise UserError(
                            _("A discount account is required to handle the product! \n%s" % 
                                (line.name))
                        )
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        res.update({'invoice_line_id': line.get('invl_id', False) })
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        res = super(AccountInvoiceLine, self)._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        if self.discount:
            self.discount_fixed = (self.quantity * self.price_unit) - self.price_subtotal
        return res

    discount_fixed = fields.Float(string='Descuento (Fijo)', digits=dp.get_precision('Discount'), translate=True,
        default=0.0, store=False, readonly=True, compute='_compute_price')


class account_invoice_tax(models.Model):
    _inherit = "account.invoice.tax"

    @api.v8
    def compute(self, invoice):
        res=super(account_invoice_tax, self).compute(invoice)
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line_ids:

            if line.discount_fixed:
                price = line.price_unit * (1 - (line.discount_fixed*100/(line.quantity * line.price_unit) if (line.quantity * line.price_unit) else 1 ) / 100.0)
                #price = line.price_unit * (1 - (line.discount_fixed or 0.0) / 100.0)
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            # taxes = line.invoice_line_tax_id.compute_all(
            #     (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
            #     line.quantity, line.product_id, invoice.partner_id)['taxes']

            taxes = line.invoice_line_tax_id.compute_all(price,line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['tax_id'] = tax['id']
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['tax_id'] = tax['id']
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])
        return tax_grouped

