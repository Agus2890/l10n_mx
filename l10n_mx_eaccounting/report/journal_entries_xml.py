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
import logging
import xml.etree.ElementTree as ET
from odoo import api
from odoo.report import report_sxw
from .report_to_file import ReportToFile
from odoo.tools.translate import _
from collections import defaultdict
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

class JournalEntries(models.AbstractModel):
    _name = 'report.l10n_mx_eaccounting.journal_entries_mx_report'

    @api.model
    def get_report_values(self, docids, data=None):
        #if not data.get('form'):
        #    raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            #'doc_ids': docs.ids,
            #'lines': self.get_lines(data.get('form')),
            #'get_taxes': self.get_taxes(),
            #'get_taxes_ret': self._get_taxes_ret,
            #'get_text_promissory': self._get_text_promissory,
            #'get_emitter_data': self._get_emitter_data,
            #'get_partner_data': self._get_partner_data,
            'get_lst_account': self.print_report_xml()
            #'legend': self._get_legend,
        }

    @api.multi
    def print_report_xml(self):
        raise ValidationError( str( self)+str("sisisiis"))

###


class journal_entries_parser(models.AbstractModel):
    """
    Parser class to build the journal entries report in format xml.
    """
    def __init__(self, name, context=None):
        super(journal_entries_parser, self).__init__(name, context=context)
        self.localcontext.update({
            "actual_context": context,
        })


class JournalEntriesXml(ReportToFile):
    """
    Class to build the journal entries report in format xml based on company,
    period and target_move.
    """
    def __init__(
        self, name, table, header=True, store=False
    ):
        """
        Set default data for report
        """
        super(JournalEntriesXml, self).__init__(
            name, table, header, store
        )

    def _get_lst_account(self,account_id):
        account_obj = self.envl['account.account']
        actual_account = account_obj.browse(account_id)
        lst_account = []
        self._fill_list_account_with_child(lst_account, actual_account)
        return tuple(lst_account)

    def _fill_list_account_with_child(self, lst_account, account):
        # no more child
        lst_account.append(account.id)
        if not account.child_id:
            return
        for child in account.child_id:
            self._fill_list_account_with_child(lst_account, child)

    def get_trans_cta(self,account_id):
        """
        Get the account number of  transaction based on the account id
        account number of  transaction is the account code.
        """
#         context = context or {}
        account_obj = self.env['account.account'].browse(account_id)
        if account_obj.sat_group_id:
            result = account_obj
        else:
            if not account_obj.parent_id:
                raise ValidationError(
                    _('Error'),
                    _('Not found Sat Code on account %s-%s. \n'
                      'Verify that the configuration of Account Sat_Group is'
                      ' correct!' % (account_obj.code, account_obj.name))
                )
            result = self.get_trans_cta(
             account_obj.parent_id.id
            )
        return result

    def get_journal_entry_type(self, journal_id):
        """
        Get the type of account journal entry based on the account journal id
        """
        journal_obj = self.env['account.journal']
        journal_entry_type = journal_obj.browse(journal_id).type
        return journal_entry_type

    def check_journal_default_credit_debit_account_id(
        self,journal_id, account_id
    ):
        """
        Checks if account_id is the default credit or debit account_id of
        account journal based on the account journal_id and account_id of
        account journal entry
        """
        journal_model = self.env['account.journal']
        journal = journal_model.browse([journal_id])[0]

        if (
            account_id == journal.default_debit_account_id.id or
            account_id == journal.default_credit_account_id.id
        ):
            return True
        return False

    def get_journal_entrie_type_xml(self, entrie):
        """
        Get the SAT type of account journal entry based on journal_type and
        # the default account for journal_id
        """
        journal_entry_type_xml = 3
        for item_line in entrie:

            if self.check_journal_default_credit_debit_account_id(
                    self.active_ids,
                    self.actual_context, item_line.get('journal_id'),
                    item_line.get('account_id')
            ):
                journal_entry_type = self.get_journal_entry_type(
                    self.active_ids,
                    self.actual_context,
                    item_line.get('journal_id')
                )

                if (journal_entry_type in ['cash', 'bank']) and item_line.get(
                    'credit'
                ):
                    return 2
                elif (
                    journal_entry_type in ['cash', 'bank']) and item_line.get(
                    'debit'
                ):
                    return 1

        return journal_entry_type_xml

    def get_journal_entry_concept(self,move_id):
        """
        Get the concept of account journal entry based on the account move id
        concept of account journal entry is the account.move ref.
        """
        move_obj = self.env['account.move']
        concept = move_obj.browse(move_id).ref or "N/A"
        return concept

    def get_trans_currency(self,currency_id):
        """
        Get the currency name of transaction based on the currency id
        """
        currency_obj = self.env['res.currency']
        currency_name = currency_obj.browse(currency_id).name
        return currency_name

    def get_check_data(
        self, move_id, journal_id, account_id,
        transaccion
    ):
        """
        Get the info of the check based on the move_id of journal entry
        """
        check_obj = self.env['account.voucher']
        # Gets the default credit account ID for the journal
        journal = self.env['account.journal'].browse(journal_id)

        # If Payment Type Not is Check, then exit
        if journal.payment_type_id.code not in ['02']:
            return

        credit_acc_id = journal.default_credit_account_id.id

        # If the used account is not the default credit account
        # don't continue
        if account_id != credit_acc_id:
            return

        # Get the bank data asociated to the journal used
        # in the journal entry
        partner_bank_data = self.get_partner_bank_data(journal_id)
        # Verify that exists bank account asociated to the journal
        if partner_bank_data:
            # Gets the info of the check data
            check_id = check_obj.search([('move_id', '=', move_id)])
            check_data = check_obj.browse(check_id)

            # Process each check if any
            for check in check_data:
                check_number = check.check_number
                # Not all vouchers are checks, skip function if not check_done
                if not check.check_done:
                    continue

                check_date = check.date
                check_amount = check.amount
                partner_name = check.partner_id.name
                partner_vat = check.partner_id.vat_split

                # Adds the check info to the xml report
                bank_acc = partner_bank_data[0].acc_number
                bank_sat_code = partner_bank_data[0].bank.sat_code

                cheque = ET.SubElement(transaccion, 'PLZ:Cheque')
                cheque.set("Num", str(check_number))
                cheque.set("BanEmisNal", (bank_sat_code).encode(
                    'utf-8', 'ignore').decode('utf-8')
                )
                cheque.set("CtaOri", (bank_acc).encode(
                    'utf-8', 'ignore').decode('utf-8')
                )
                cheque.set("Fecha", str(check_date))
                cheque.set("Monto", str(check_amount))
                cheque.set("Benef", (partner_name).encode(
                    'utf-8', 'ignore').decode('utf-8')
                )
                cheque.set("RFC", (partner_vat).encode(
                    'utf-8', 'ignore').decode('utf-8')
                )
        return True

    def get_partner_bank_data(self,journal_id):
        """
        Get the info of the bank account based on the journal_id of
        journal entry
        """
        bank_obj = self.env['res.partner.bank']
        bank_id = bank_obj.search([('journal_id', '=', journal_id)])
        bank_data = bank_obj.browse(bank_id)
        return bank_data

    def get_invoice_data(
        self,acc_move_line, journal_entry_type_xml,
        transaccion
    ):
        """
        Get the info of the Invoice based on the move_id of journal entry
        """
        invoice_obj = self.env['account.invoice']

        filters = []
        if (
            journal_entry_type_xml in [1, 2] and
            (acc_move_line.get('reconcile_id') or
             acc_move_line.get('reconcile_partial_id'))
        ):
            # if journal entry in Ingreso|Egreso
            reconcile_field = acc_move_line.get(
                'reconcile_id') and 'reconcile_id' or 'reconcile_partial_id'
            reconcile_value = acc_move_line.get(
                'reconcile_id') or acc_move_line.get('reconcile_partial_id')

            filters = [(reconcile_field, '=', reconcile_value),
                       ('journal_id', '!=', acc_move_line.get('journal_id'))]

            move_obj = self.env['account.move.line']
            move_id = move_obj.search(filters)
            if move_id:
                move_data = move_obj.browse(move_id)

                for move in move_data:
                    filters = [
                        ('move_id', '=', move.move_id.id),
                        ('account_id', '=', acc_move_line.get('account_id'))
                    ]
            else:
                return False

        elif journal_entry_type_xml in [3]:
            filters = [('move_id', '=', acc_move_line.get('move_id')),
                       ('account_id', '=', acc_move_line.get('account_id'))]
        else:
            return False

        invoice_id = invoice_obj.search(filters)
        invoice_data = invoice_obj.browse(invoice_id)

        # Process each invoice if any
        for invoice in invoice_data:
            # Only add information about Comprobante
            # if there is an UUID at current invoice
            if invoice.cfdi_folio_fiscal:
                if not invoice.partner_id.vat_split:
                    raise ValidationError(
                        _('Error'),
                        _('Partner %s do not have a VAT number assigned')
                        % invoice.partner_id.name
                    )
                comprobante = ET.SubElement(transaccion, 'PLZ:CompNal')
                comprobante.set('MontoTotal', str(invoice.amount_total))
                comprobante.set('RFC', invoice.partner_id.vat_split)
                comprobante.set('UUID_CFDI', invoice.cfdi_folio_fiscal)
                if invoice.currency_id.name != 'MXN':
                    comprobante.set('Moneda', invoice.currency_id.name)
                    comprobante.set('TipCamb', str(invoice.rate))
        return True

    def get_transferencia_data(
        self,acc_move_line, journal_entry_type_xml,
        transaccion
    ):
        """
        Get the info of the Transferencia based on the move_id of journal entry
        """
#         context = context or {}
        payment_obj = self.env['account.voucher']
        # Gets the default credit account ID for the journal
        journal = self.env['account.journal'].browse(acc_move_line.get('journal_id'))

        # If Payment Type Not is Transfer, then exit
        if journal.payment_type_id.code not in ['03']:
            return

        credit_acc_id = journal.default_credit_account_id.id

        # If the used account is not the default credit account
        # don't continue
        if acc_move_line.get('account_id') != credit_acc_id:
            return

        payment_line_ids = payment_obj.search([('move_id', '=', acc_move_line.get('move_id'))])
        
        payment_line_data = payment_obj.browse(payment_line_ids)

        # Process each payment line if any
        for payment_line in payment_line_data:
            transferencia = ET.SubElement(transaccion, 'PLZ:Transferencia')
            partnerBank = payment_line.partner_bank_id
            companyBank = payment_line.journal_id.res_partner_bank_id[0]
            partner = payment_line.partner_id

            # If dealing with income money
            rfc = partner.vat_split or 'N/A'
            if journal_entry_type_xml == 1:
                cta_orig = partnerBank.acc_number
                banco_orig = partnerBank.bank.sat_code
                cta_dest = companyBank.acc_number
                banco_dest = companyBank.bank.sat_code
                benef = companyBank.partner_id.name
            # If dealing with out money
            elif journal_entry_type_xml == 2:
                cta_orig = companyBank.acc_number
                banco_orig = companyBank.bank.sat_code
                cta_dest = partnerBank.acc_number
                banco_dest = partnerBank.bank.sat_code
                benef = partnerBank.partner_id.name

            transferencia.set('CtaOri', cta_orig)
            transferencia.set('BancoOriNal', banco_orig)
            transferencia.set('Monto', str(payment_line.amount))
            transferencia.set('CtaDest', cta_dest)
            transferencia.set('BancoDestNal', banco_dest)
            transferencia.set('Benef', benef)
            transferencia.set('RFC', rfc)
            transferencia.set('Fecha', payment_line.date)
        return

    def get_otr_metodo_pago(
        self,acc_move_line, journal_entry_type_xml,
        transaccion
    ):
        """
        Get the info of the otrMetodoPago based on the move_id of journal entry
        """
#         context = context or {}
        payment_obj = self.env['account.voucher']
        # Gets the default credit account ID for the journal
        journal = self.env['account.journal'].browse(acc_move_line.get('journal_id'))

        credit_acc_id = journal.default_credit_account_id.id

        # If the used account is not the default credit account
        # don't continue
        if acc_move_line.get('account_id') != credit_acc_id:
            return

        if not journal.payment_type_id:
            raise ValidationError(
                    _('Error'),
                    _('Journal %s do not have set a Payment Type')
                    % journal.name
                )

        # If Payment Type is Check or Transfer, then exit
        if journal.payment_type_id.code in ['02', '03']:
            return

        payment_line_ids = payment_obj.search([('move_id', '=', acc_move_line.get('move_id'))])
        payment_line_data = payment_obj.browse(payment_line_ids)

        # Process each payment line if any
        for payment_line in payment_line_data:
            otrmetodopago = ET.SubElement(transaccion, 'PLZ:OtrMetodoPago')

            # MetPagoPol
            # Fecha
            # Benef
            # RFC
            # Monto
            # Moneda
            # TipCamb

            partnerBank = payment_line.partner_bank_id
            partner = payment_line.partner_id

            # If dealing with income money
            rfc = partner.vat_split or 'N/A'
            benef = partner.name

            otrmetodopago.set('MetPagoPol', str(journal.payment_type_id.code))
            otrmetodopago.set('Fecha', payment_line.date)
            otrmetodopago.set('Benef', benef)
            otrmetodopago.set('RFC', rfc)
            otrmetodopago.set('Monto', str(payment_line.amount))

            if payment_line.is_multi_currency:
                otrmetodopago.set('Moneda', str(payment_line.currency_id.name))
                otrmetodopago.set('TipCamb', str(payment_line.payment_rate))

        return


    def generate_report(self, data, objects):
        """
        Build journal entries report in format xml based on company,
        period and target_move.
        """
        context = self.actual_context
        import tempfile

        account_move_model = self.env['account.move']

        Etree = ET.ElementTree()
        # #Begin of Sql query Section
        period_id = data["form"]["period_id"]
        target_move = data["form"]["target_move"]
        period_obj = self.env['account.period']
        period = period_obj.browse(
            period_id,
            context=self.actual_context
        )

        sql_select = """
        SELECT al.debit,al.credit,al.amount_currency,al.date,al.journal_id,
        al.ref,al.move_id,al.name,al.currency_id,al.account_id,
        al.reconcile_id, al.reconcile_partial_id
        FROM account_move_line al """
        sql_where = """
        WHERE al.period_id =  %(period_id)s
        AND al.state = 'valid'
        AND al.account_id in %(account_id)s """
        search_params = {
            'period_id': period_id,
            'account_id': self._get_lst_account(
                data['form']['account_id'],
                context=context
            )
        }
        sql_joins = ''
        sql_orderby = 'ORDER BY al.move_id'
        if target_move == 'posted':
            sql_joins = 'LEFT JOIN account_move am ON move_id = am.id '
            sql_where += """ AND am.state = %(target_move)s"""
            search_params.update({'target_move': target_move})
        query_sql = ' '.join((sql_select, sql_joins, sql_where, sql_orderby))
        self.cr.execute(query_sql, search_params)
        lines = self.cr.dictfetchall()
        # #End of Sql query Section
        if not lines:
            raise ValidationError(
                _('Error'),
                _('Not found Journal Entries for this Period.\n'
                  'Choose another Period!')
            )
        # if Journal Entries have lines will create the xml report
        # Create main journal entries node
        type_request = data["form"]["type_request"]
        order_num = data["form"]["order_num"]
        pro_num = data["form"]["pro_num"]
        from datetime import datetime
        time_period = datetime.strptime(period.date_start, "%Y-%m-%d")

        polizas = ET.Element('PLZ:Polizas')
        # namespace
        polizas.set("xsi:schemaLocation",
                    "www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo/PolizasPeriodo_1_1.xsd")
        polizas.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        polizas.set("xmlns:PLZ", "www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo")

        polizas.set('Version', '1.1')
        polizas.set('RFC', self.company.partner_id.vat_split)
        polizas.set('Mes', str(time_period.month).rjust(2, '0'))
        polizas.set('Anio', str(time_period.year))
        polizas.set('TipoSolicitud', type_request)
        if order_num:
            polizas.set('NumOrden', order_num)
        if pro_num:
            polizas.set('NumTramite', pro_num)
        Etree._setroot(polizas)

        # Groups of account move based on move id,
        # each group is one journal entries
        groups = defaultdict(list)
        for line in lines:
            groups[line.get('move_id')].append(line)
        for move_id in groups.keys():
            # Load account.move object for current move lines
            move = account_move_model.browse(
                move_id, context=context
            )
            cumul_debit = 0.0
            cumul_credit = 0.0
            poliza = ET.SubElement(polizas, 'PLZ:Poliza')

            # Check for SAT journal type using
            journal_entry_type_xml = self.get_journal_entrie_type_xml(
                parser, groups[move_id]
            )

            for item_line in groups[move_id]:
                # required fields on journal entry node
                cumul_debit += item_line.get('debit') or 0.0
                cumul_credit += item_line.get('credit') or 0.0
                journal_id = item_line.get('journal_id')
                # #Begin on transaction node
                trans_concept = item_line.get('name')
                acccta = self.get_trans_cta(
                    item_line.get('account_id'), context=context
                )
                transaccion = ET.SubElement(poliza, 'PLZ:Transaccion')
                transaccion.set("NumCta", acccta.code)
                transaccion.set("DesCta", acccta.name)
                transaccion.set("Concepto", (trans_concept).encode(
                    'utf-8', 'ignore').decode('utf-8')
                )
                transaccion.set("Debe", str(item_line.get('debit')))
                transaccion.set("Haber", str(item_line.get('credit')))

                # Begin on journal entry node
                if journal_entry_type_xml in [2]:
                    # Get the check data related to the journal entry move
                    self.get_check_data(
                        self.active_ids,
                        context, move_id, journal_id,
                        acccta.id, transaccion
                    )
                    # #End of Check section
                # # Begin for Invoice CFDI Section
                self.get_invoice_data(
                    self.active_ids,
                    context, item_line, journal_entry_type_xml,
                    transaccion
                )
                # # End for Invoice CFDI Section

                # Get the Transferencia or otrMetodoPago data related for the Journal Entry move
                if journal_entry_type_xml in [1, 2]:
                    self.get_transferencia_data(
                        item_line, journal_entry_type_xml,
                        transaccion, context=context,
                    )

                    self.get_otr_metodo_pago(
                        item_line, journal_entry_type_xml,
                        transaccion, context=context,
                    )
                # # End of Transferencia Section
                # #End on transaction node
            journal_entry_concept = self.get_journal_entry_concept(
                self.active_ids,
                context, move_id
            )

            concept_description = ("%s | $%s | $%s") % (
                (journal_entry_concept).encode(
                    'utf-8', 'ignore').decode(
                    'utf-8'), cumul_debit, cumul_credit
            )
            poliza.set("NumUnIdenPol", move.name)
            poliza.set("Concepto", concept_description)
            poliza.set("Fecha", move.date)
            # #End on journal entry node
        # Write data into temporal file
        with tempfile.NamedTemporaryFile(delete=False) as report:
            Etree.write(report.name, encoding='UTF-8')
            self.fname = report.name

        return
    
#     @api.model
#     def render_html(self, docids, data=None):
#         if not data.get('form'):
#             raise UserError(_("Form content is missing, this report cannot be printed."))
# 
#         target_move = data['form'].get('target_move', 'all')
#         sort_selection = data['form'].get('sort_selection', 'date')
# 
#         res = {}
#         for journal in data['form']['journal_ids']:
#             res[journal] = self.with_context(data['form'].get('used_context', {})).lines(target_move, journal, sort_selection, data)
#         docargs = {
#             'doc_ids': data['form']['journal_ids'],
#             'doc_model': self.env['account.journal'],
#             'data': data,
#             'docs': self.env['account.journal'].browse(data['form']['journal_ids']),
#             'time': time,
#             'lines': res,
#             'sum_credit': self._sum_credit,
#             'sum_debit': self._sum_debit,
#             'get_taxes': self._get_taxes,
#         }
#         return self.env['report'].render('l10n_mx_eaccounting.journal_entries', docargs)


# JournalEntriesXml(
#     'report.journal.entries.xml',
#     'account.account',
#     parser=journal_entries_parser
# )
