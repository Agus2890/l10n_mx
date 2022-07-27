# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
import odoo.addons.decimal_precision as dp


class AccountMove(models.Model):
    _inherit = "account.move"

    def reverse_moves(self, date=None, journal_id=None):
        date = date or fields.Date.today()
        reversed_moves = self.env['account.move']
        if self.company_id.currency_id.name != 'MXN':
            for ac_move in self:
                #unreconcile all lines reversed
                aml = ac_move.line_ids.filtered(lambda x: x.account_id.reconcile or x.account_id.internal_type == 'liquidity')
                aml.remove_move_reconcile()
                reversed_move = ac_move._reverse_move(date=date,
                                                      journal_id=journal_id)
                reversed_moves |= reversed_move
                #reconcile together the reconciliable (or the liquidity aml) and their newly created counterpart
                for account in set([x.account_id for x in aml]):
                    to_rec = aml.filtered(lambda y: y.account_id == account)
                    to_rec |= reversed_move.line_ids.filtered(lambda y: y.account_id == account)
                    #reconciliation will be full, so speed up the computation by using skip_full_reconcile_check in the context
                    to_rec.with_context(skip_full_reconcile_check=True).reconcile()
                    to_rec.force_full_reconcile()
            if reversed_moves:
                reversed_moves._post_validate()
                reversed_moves.post()
                return [x.id for x in reversed_moves]
        return []


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        # Empty self can happen if the user tries to reconcile entries which are already reconciled.
        # The calling method might have filtered out reconciled lines.
        if not self:
            return True

        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        partners = set()
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.account_id.internal_type in ('receivable', 'payable')):
                partners.add(line.partner_id.id)
            if (line.matched_debit_ids or line.matched_credit_ids) and line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries!'))
        if len(set(all_accounts)) > 1 and all_accounts[0].company_id.currency_id.name != 'MXN':
            raise UserError(_('Entries are not of the same account!'))
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (all_accounts[0].name, all_accounts[0].code))

        #reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        #if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
            #add writeoff line to reconcile algo and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
            return writeoff_to_reconcile
        return True

    def force_full_reconcile(self):
        """ After running the manual reconciliation wizard and making full reconciliation, we need to run this method to create
            potentially exchange rate entries that will balance the remaining amount_residual_currency (possibly several aml in
            different currencies).

            This ensure that all aml in the full reconciliation are reconciled (amount_residual = amount_residual_currency = 0).
        """
        aml_to_balance_currency = {}
        partial_rec_set = self.env['account.partial.reconcile']
        maxdate = '0000-00-00'

        # gather the max date for the move creation, and all aml that are unbalanced
        for aml in self:
            maxdate = max(aml.date, maxdate)
            if aml.amount_residual_currency:
                if aml.currency_id not in aml_to_balance_currency:
                    aml_to_balance_currency[aml.currency_id] = [self.env['account.move.line'], 0]
                aml_to_balance_currency[aml.currency_id][0] |= aml
                aml_to_balance_currency[aml.currency_id][1] += aml.amount_residual_currency
            partial_rec_set |= aml.matched_debit_ids | aml.matched_credit_ids

        #create an empty move that will hold all the exchange rate adjustments
        exchange_move = False
        if aml_to_balance_currency and any([residual for dummy, residual in aml_to_balance_currency.values()]) and self.company_id.currency_id.name != 'MXN':
            exchange_move = self.env['account.move'].create(
                self.env['account.full.reconcile']._prepare_exchange_diff_move(move_date=maxdate, company=self[0].company_id))

        for currency, values in aml_to_balance_currency.items():
            aml_to_balance = values[0]
            total_amount_currency = values[1]
            if total_amount_currency:
                #eventually create journal entries to book the difference due to foreign currency's exchange rate that fluctuates
                aml_recs, partial_recs = self.env['account.partial.reconcile'].create_exchange_rate_entry(aml_to_balance, 0.0, total_amount_currency, currency, exchange_move)

                #add the ecxhange rate line and the exchange rate partial reconciliation in the et of the full reconcile
                self |= aml_recs
                partial_rec_set |= partial_recs
            else:
                aml_to_balance.reconcile()

        if exchange_move:
            exchange_move.post()

        #mark the reference on the partial reconciliations and the entries
        #Note that we should always have all lines with an amount_residual and an amount_residual_currency equal to 0
        partial_rec_ids = [x.id for x in list(partial_rec_set)]
        self.env['account.full.reconcile'].create({
            'partial_reconcile_ids': [(6, 0, partial_rec_ids)],
            'reconciled_line_ids': [(6, 0, self.ids)],
            'exchange_move_id': exchange_move.id if exchange_move else False,
        })


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    def _compute_partial_lines(self):
        if self._context.get('skip_full_reconcile_check'):
            #when running the manual reconciliation wizard, don't check the partials separately for full
            #reconciliation or exchange rate because it is handled manually after the whole processing
            return self
        #check if the reconcilation is full
        #first, gather all journal items involved in the reconciliation just created
        aml_set = aml_to_balance = self.env['account.move.line']
        total_debit = 0
        total_credit = 0
        total_amount_currency = 0
        #make sure that all partial reconciliations share the same secondary currency otherwise it's not
        #possible to compute the exchange difference entry and it has to be done manually.
        self.ensure_one()
        currency = self.debit_move_id.currency_id or self.credit_move_id.currency_id or None
        more_than_1_currency = False
        maxdate = '0000-00-00'

        seen = set()
        todo = set(self)
        while todo:
            partial_rec = todo.pop()
            seen.add(partial_rec)
            if partial_rec.debit_move_id.currency_id != currency or partial_rec.credit_move_id.currency_id != currency:
                #There's more than 1 secondary currency involved, which means that we can use the total_debit
                # and total_credit comparison (otherwise we cannot, as we have to rely only on the amount in
                # secondary currency to deal with the case stated in test_partial_reconcile_currencies_02)
                more_than_1_currency = True
            if partial_rec.currency_id != currency:
                #no exchange rate entry will be created
                currency = False
            for aml in [partial_rec.debit_move_id, partial_rec.credit_move_id]:
                if aml not in aml_set:
                    if aml.amount_residual or aml.amount_residual_currency:
                        aml_to_balance |= aml
                    maxdate = max(aml.date, maxdate)
                    total_debit += aml.debit
                    total_credit += aml.credit
                    aml_set |= aml
                    if aml.currency_id and aml.currency_id == currency:
                        total_amount_currency += aml.amount_currency
                    elif partial_rec.currency_id and partial_rec.currency_id == currency:
                        #if the aml has no secondary currency but is reconciled with other journal item(s) in secondary currency, the amount
                        #in secondary currency is recorded on the partial rec. That allows us to consider it, in order to check if the
                        # reconciliation is total
                        total_amount_currency += aml.balance > 0 and partial_rec.amount_currency or - partial_rec.amount_currency

                for x in aml.matched_debit_ids | aml.matched_credit_ids:
                    if x not in seen:
                        todo.add(x)

        partial_rec_ids = [x.id for x in seen]
        aml_ids = aml_set.ids
        #if the total debit and credit are equal, or the total amount in currency is 0, the reconciliation is full
        digits_rounding_precision = aml_set[0].company_id.currency_id.rounding
        if (currency and float_is_zero(total_amount_currency, precision_rounding=currency.rounding)) or \
           ((currency is None or more_than_1_currency) and float_compare(total_debit, total_credit, precision_rounding=digits_rounding_precision) == 0):
            exchange_move_id = False
            if aml_to_balance and self.company_id.currency_id.name != 'MXN':
                exchange_move = self.env['account.move'].create(
                    self.env['account.full.reconcile']._prepare_exchange_diff_move(move_date=maxdate, company=aml_to_balance[0].company_id))
                #eventually create a journal entry to book the difference due to foreign currency's exchange rate that fluctuates
                rate_diff_amls, rate_diff_partial_rec = self.create_exchange_rate_entry(aml_to_balance, total_debit - total_credit, total_amount_currency, currency or aml_to_balance[0].currency_id, exchange_move)
                aml_ids += rate_diff_amls.ids
                partial_rec_ids += rate_diff_partial_rec.ids
                exchange_move.post()
                exchange_move_id = exchange_move.id
            #mark the reference of the full reconciliation on the partial ones and on the entries
            self.env['account.full.reconcile'].create({
                'partial_reconcile_ids': [(6, 0, partial_rec_ids)],
                'reconciled_line_ids': [(6, 0, aml_ids)],
                'exchange_move_id': exchange_move_id,
            })

    # @api.model
    # def create(self, vals):
    #     aml = []
    #     if vals.get('debit_move_id', False):
    #         aml.append(vals['debit_move_id'])
    #     if vals.get('credit_move_id', False):
    #         aml.append(vals['credit_move_id'])
    #     # Get value of matched percentage from both move before reconciliating
    #     lines = self.env['account.move.line'].browse(aml)
    #     lines._payment_invoice_match()
    #     tax_cash_basis_entry = not self.env.context.get('skip_tax_cash_basis_entry') and lines[0].account_id.internal_type in ('receivable', 'payable')
    #     if tax_cash_basis_entry:
    #         percentage_before_rec = lines._get_matched_percentage()
    #     # Reconcile
    #     res = super(AccountPartialReconcile, self).create(vals)
    #     # if the reconciliation is a matching on a receivable or payable account, eventually create a tax cash basis entry
    #     if tax_cash_basis_entry and self.company_id.currency_id.name != 'MXN':
    #         res.create_tax_cash_basis_entry(percentage_before_rec)
    #     res._compute_partial_lines()
    #     return res
