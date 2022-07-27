# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class AccountAbstractPayment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    line_ids = fields.One2many('account.payment.line', 'payment_id', 'Payment lines',
        help='Please select invoices for this partner for the payment')
    selected_inv_total = fields.Float(compute='compute_selected_invoice_total',
        store=True, string='Assigned Amount')
    balance = fields.Float(compute='_compute_balance', string='Balance')


class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'

    invoice_id = fields.Many2one('account.move', 'Invoice')
    payment_id = fields.Many2one('account.payment', 'Related Payment')
    partner_id = fields.Many2one(related='invoice_id.partner_id', string='Partner')
    amount_total = fields.Monetary('Amount Total')
    residual = fields.Monetary('Amount Due')
    amount = fields.Monetary('Amount To Pay',
        help="Enter amount to pay for this invoice, supports partial payment")
    actual_amount = fields.Float(compute='compute_actual_amount',
        string='Actual amount paid', help="Actual amount paid in journal currency")
    date_invoice = fields.Date(related='invoice_id.date_invoice', string='Invoice Date')
    currency_id = fields.Many2one(related='invoice_id.currency_id', string='Currency')
    amount_original = fields.Monetary(string='Original Amount')
    amount_unreconciled = fields.Monetary(string='Open Balance')
    reconcile = fields.Boolean(string='Full Reconcile')
    amount_payment = fields.Monetary(string='Pay complement',
        help="Enter amount to pay for this complement")

    @api.depends('amount', 'payment_id.payment_date')
    def compute_actual_amount(self):
        for line in self:
            if line.amount > 0 and not line.reconcile:
                line.actual_amount = \
                    line.currency_id.with_context(date=line.payment_id.payment_date).compute(
                        line.amount, line.payment_id.currency_id)
            elif line.amount > 0 and line.reconcile:
                line.actual_amount = line.amount_unreconciled
            else:
                line.actual_amount = 0.0

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            if line.amount < 0:
                raise UserError(_('Amount to pay can not be less than 0! (Invoice code: %s)')
                    % line.invoice_id.number)
            if line.amount > line.residual:
                raise UserError(_('"Amount to pay" can not be greater than than "Amount '
                                  'Due" ! (Invoice code: %s)')
                                % line.invoice_id.number)

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        for line in self:
            if line.invoice_id:
                line.amount_total = line.invoice_id.amount_total
                line.residual = line.invoice_id.residual
            else:
                line.amount_total = 0.0
                line.residual = 0.0
                line.amount_original = 0.0

    @api.onchange('reconcile')
    def onchange_amount(self):
        for line in self:
            if line.reconcile:
                line.amount = line.invoice_id.residual
                if line.residual == 0.0:
                    line.residual = line.invoice_id.residual
            else:
                line.amount = 0.0


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    line_ids = fields.One2many(
        'account.payment.line', 'payment_id', 'Payment lines',
        help='Please select invoices for this partner for the payment')
    selected_inv_total = fields.Float(
        compute='compute_selected_invoice_total',
        store=True, string='Assigned Amount')
    balance = fields.Float(
        compute='_compute_balance', string='Balance')
    move_id = fields.Many2one(
        'account.move', string='Account Entry', copy=False)
    move_ids = fields.One2many(
        'account.move.line', related='move_id.line_ids', string='Journal Items',
        readonly=True, copy=False)
    # payment_rate_currency_id = fields.Many2one('res.currency', string='Payment Rate Currency', required=True, readonly=True, states={'draft':[('readonly',False)]})
    payment_rate = fields.Float(string='Exchange Rate', digits=(12,10), required=True, readonly=True, states={'draft': [('readonly', False)]}, default=1.0, 
        help='The specific rate that will be used, in this payment, between the selected currency (in \'Payment Rate Currency\' field)  and the payment currency.')

    @api.depends('line_ids', 'line_ids.reconcile', 'line_ids.amount')#, 'amount'
    def _compute_balance(self):
        for payment in self:
            total = 0.0
            for line in payment.line_ids:
                total += line.actual_amount
            if payment.amount > total:
                balance = payment.amount - total
            else:
                balance = payment.amount - total
            payment.balance = payment.currency_id.with_context(
                date=payment.payment_date).compute(balance, self.currency_id)
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}            

    @api.depends('line_ids', 'line_ids.amount', 'line_ids.actual_amount')
    def compute_selected_invoice_total(self):
        for payment in self:
            total = 0.0
            for line in payment.line_ids:
                total += line.actual_amount
            payment.selected_inv_total = total

    @api.onchange('partner_id', 'payment_type')
    def onchange_partner_id(self):
        Invoice = self.env['account.move']
        PaymentLine = self.env['account.payment.line']
        if self.partner_id:
            partners_list = self.partner_id.child_ids.ids
            partners_list.append(self.partner_id.id)
            line_ids = []
            type = ''
            if self.payment_type == 'outbound':
                type = 'in_invoice'
            elif self.payment_type == 'inbound':
                type = 'out_invoice'
            invoices = Invoice.search([('partner_id', 'in', partners_list),
                ('state', 'in', ('open', )), ('type', '=', type)], order="date_invoice")
            for invoice in invoices:
                ml = invoice.move_id.line_ids.filtered(lambda r: r.account_id.id == invoice.account_id.id)
                data = {
                    'invoice_id': invoice.id,
                    'amount_total': invoice.amount_total,
                    'residual': invoice.residual,
                    'amount_original': ml.debit if invoice.currency_id.id != self.journal_id.currency_id.id else ml.amount_currency,
                    'amount_unreconciled': ml.amount_residual if invoice.currency_id.id != self.journal_id.currency_id.id else ml.amount_residual_currency,
                    'amount': 0.0,
                    'date_invoice': invoice.date_invoice,
                }
                line = PaymentLine.create(data)
                line_ids.append(line.id)
            self.line_ids = [(6, 0, line_ids)]
        else:
            if self.line_ids:
                for line in self.line_ids:
                    line.unlink()
            self.line_ids = []

    # @api.onchange('amount')
    # def onchange_amount(self):
    #     ''' Function to reset/select invoices on the basis of invoice date '''
    #     if self.amount > 0 and not self.selected_inv_total > 0:
    #         total_amount = self.amount
    #         for line in self.line_ids:
    #             if total_amount > 0:
    #                 conv_amount = self.currency_id.with_context(
    #                     date=self.payment_date).compute(total_amount, line.currency_id)
    #                 if line.residual < conv_amount:
    #                     line.amount = line.residual
    #                     if line.currency_id.id == self.currency_id.id:
    #                         total_amount -= line.residual
    #                     else:
    #                         spend_amount = line.currency_id.with_context(
    #                             date=self.payment_date).compute(
    #                             line.residual, self.currency_id)
    #                         total_amount -= spend_amount
    #                 else:
    #                     line.amount = self.currency_id.with_context(
    #                         date=self.payment_date).compute(total_amount, line.currency_id)
    #                     total_amount = 0
    #             else:
    #                 line.amount = 0.0
    #     if (self.amount <= 0):
    #         for line in self.line_ids:
    #             line.amount = 0.0

    @api.onchange('line_ids')
    def _onchange_invoice(self):
        invoice_ids = []
        if self.line_ids and self.payment_type == 'inbound':
            self.invoice_ids = [(6, 0, [])]
            for rec in self.line_ids:
                invoice_ids.append(rec.invoice_id.id)
            number = len(invoice_ids)    
            if invoice_ids:
                self.invoice_ids = [(6, 0, invoice_ids)] if number >= 1 else [(6, 0, [])]

    # @api.multi
    # @api.constrains('amount', 'selected_inv_total', 'line_ids', 'rate_updated')
    # def _check_invoice_amount(self):
    #     ''' Function to validate if user has selected more amount invoices than payment '''
    #     return True
    #     # for payment in self:
    #     #     if payment.line_ids:
    #     #         if (payment.selected_inv_total - payment.amount) > 0.05:
    #     #             raise UserError(_('You cannot select more value invoices than the payment amount'))

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
            OVERRIDDEN: generated multiple journal items for each selected invoice
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            # if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date)._compute_amount_fields(
            amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())
        # Custom Code
        counterpart_aml = False
        invoice_reconcile_amount = 0
        sum_credit, sum_debit = 0, 0
        invoice_dict = {}
        # Creating invoice wise move lines
        if self.line_ids:
            line_ids = self.line_ids.filtered(lambda r:abs(r.amount) > 0 )
            for line in line_ids:
                inv = line.invoice_id
                inv_amount = abs(line.amount) * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
                inv_amount1 = abs(line.actual_amount) * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
                invoice_currency = inv.currency_id
                debit1, credit1, amount_currency1, currency_id1 = aml_obj.with_context(
                    date=self.payment_date)._compute_amount_fields(
                    inv_amount1, self.currency_id, self.company_id.currency_id)
                counterpart_aml_dict1 = self._get_shared_move_line_vals(
                    debit1, credit1, amount_currency1, move.id, False)
                counterpart_aml_dict1.update(
                    self._get_counterpart_move_line_vals(False))
                _logger.info("===================================================1: %s " % (counterpart_aml_dict1))
                counterpart_aml_dict1.update({'currency_id': currency_id1})
                # Validate invoice account at payment
                if counterpart_aml_dict1['account_id'] != line.invoice_id.account_id.id:
                    counterpart_aml_dict1['account_id'] = line.invoice_id.account_id.id
                counterpart_aml1 = aml_obj.create(counterpart_aml_dict1)
                invoice_dict[counterpart_aml1] = inv
                # inv.register_payment(counterpart_aml1)
                invoice_reconcile_amount += inv_amount
                sum_credit += credit1
                sum_debit += debit1
            # Creating journal item for remaining payment amount
            remaining_amount = 0
            if self.payment_type in ('outbound', 'transfer'):
                remaining_amount = amount - self.selected_inv_total
            else:
                remaining_amount = abs(amount) - self.selected_inv_total
                #Pago de cliente                
            # if round(abs(remaining_amount), 6) > 0.1:
            #     # remaining_amount = line.currency_id.compute(remaining_amount, self.currency_id)
            #     remaining_amount = remaining_amount * (
            #         self.payment_type in ('outbound', 'transfer') and 1 or -1)
            #     debit1, credit1, amount_currency1, currency_id1 = aml_obj.with_context(
            #         date=self.payment_date)._compute_amount_fields(
            #         remaining_amount, self.currency_id, self.company_id.currency_id)
            #     counterpart_aml_dict1 = self._get_shared_move_line_vals(
            #     debit1, credit1, amount_currency1, move.id, False)
            #     counterpart_aml_dict1.update(
            #         self._get_counterpart_move_line_vals(False))
            #     counterpart_aml_dict1.update({'currency_id': currency_id1})
            #     counterpart_aml1 = aml_obj.create(counterpart_aml_dict1)
            #     sum_credit += credit1
            #     sum_debit += debit1
            # Creating move line for currency exchange/conversion rate difference
            if self.payment_type in ('outbound', 'transfer'):
                amount_diff = debit - sum_debit
            else:
                amount_diff = credit - sum_credit
            if round(abs(amount_diff), 6) > 0:
                conversion = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                debit_co, credit_co, amount_currency_co, currency_id_co = aml_obj.with_context(
                    date=self.payment_date)._compute_amount_fields(
                    amount_diff, self.currency_id, self.company_id.currency_id)

                conversion['name'] = _('Currency exchange rate difference')
                conversion['account_id'] = amount_diff > 0 and \
                                           self.company_id.currency_exchange_journal_id.default_debit_account_id.id or \
                                           self.company_id.currency_exchange_journal_id.default_credit_account_id.id
                if self.writeoff_account_id:
                    conversion['account_id'] = self.writeoff_account_id.id
                if amount_diff > 0:
                    conversion['debit'] = round(abs(amount_diff), 6) if self.payment_type in ('outbound', 'transfer') else 0
                    conversion['credit'] = round(abs(amount_diff), 6) if self.payment_type not in ('outbound', 'transfer') else 0
                else:
                    conversion['debit'] = round(abs(amount_diff), 6) if self.payment_type not in ('outbound', 'transfer') else 0
                    conversion['credit'] = round(abs(amount_diff), 6)if self.payment_type in ('outbound', 'transfer') else 0
                # if not self.payment_type in ('outbound', 'transfer'):
                #     conversion['debit'] = round(abs(amount_diff), 6)
                #     conversion['credit'] = 0
                # else:
                #     conversion['debit'] = 0
                #     conversion['credit'] = round(abs(amount_diff), 6)
                conversion['currency_id'] = currency_id_co
                conversion['payment_id'] = self.id
                _logger.info("===================================================2: %s " % (conversion))
                # raise UserError( str(self.payment_type ))
                aml_obj.create(conversion)
                sum_credit += round(abs(amount_diff), 6)
                sum_debit += round(abs(amount_diff), 6)
        else:
            # Default code
            # Write line corresponding to invoice payment
            counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
            counterpart_aml_dict.update({'currency_id': currency_id})
            _logger.info("===================================================3: %s " % (counterpart_aml_dict))
            counterpart_aml = aml_obj.create(counterpart_aml_dict)
            self.invoice_ids.register_payment(counterpart_aml)

        # # Default code
        # # Reconcile with the invoices
        # if self.payment_difference_handling == 'reconcile' and self.payment_difference:
        #     writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
        #     debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
        #         date=self.payment_date)._compute_amount_fields(
        #         self.payment_difference, self.currency_id, self.company_id.currency_id)
        #     writeoff_line['name'] = _('Counterpart')
        #     writeoff_line['account_id'] = self.writeoff_account_id.id
        #     writeoff_line['debit'] = debit_wo
        #     writeoff_line['credit'] = credit_wo
        #     writeoff_line['amount_currency'] = amount_currency_wo
        #     writeoff_line['currency_id'] = currency_id
        #     writeoff_line = aml_obj.create(writeoff_line)
        #     # if counterpart_aml['debit']:
        #     #     counterpart_aml['debit'] += credit_wo - debit_wo
        #     # if counterpart_aml['credit']:
        #     #     counterpart_aml['credit'] += debit_wo - credit_wo
        #     # counterpart_aml['amount_currency'] -= amount_currency_wo
        # Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        _logger.info("===================================================: %s " % (liquidity_aml_dict))
        aml_obj.create(liquidity_aml_dict)

        diff=self.payment_difference

        move.post()
        self.move_id = move.id
        for key, val in invoice_dict.items():
            val.register_payment(key)
        # Delete account invoice line in paid
        if move and self.invoice_ids:
            account_ids = self.invoice_ids.mapped('invoice_line_ids').mapped('account_id').ids
            line_ids = move.line_ids.filtered(lambda r: r.account_id.id in account_ids)
            move.write({'state': 'draft'})
            line_ids.unlink()
            move.write({'state': 'posted'})
        return move

    def post(self):
        res = super(AccountPayment, self).post()
        if len(self.move_line_ids.mapped('move_id')) == 1:
            move_pay = self.env['account.move'].search([('ref', '=', self.move_line_ids.mapped('move_id').name), ('line_ids', '=', False)])
            move_pay.unlink()
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update(line_ids=[], invoice_total=0.0)
        return super(AccountPayment, self).copy(default)
