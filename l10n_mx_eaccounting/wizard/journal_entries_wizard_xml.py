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
from odoo import models,api
from odoo import fields
from odoo.tools.translate import _
import xml.etree.ElementTree as ET

import re
import logging
# from duplicity.tempdir import default
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class journal_entries_wizard_xml(models.TransientModel):
    _name = 'journal.entries.wizard.xml'
    _inherit = "account.common.report"
    
#     def _get_account_ids(self):
#         res = False
#         if self._context.get('active_model', False) == 'account.account' and self._context.get('active_ids', False):
#             res = self._context['active_ids']
#         return res
#     
    
    #fiscalyear_id
    date_range_id= fields.Many2one(
            'date.range', 'Fiscal Year',
            help=_('Select period for your chart report'))
    date_from=fields.Date(string="Fecha Inicio",required=True)
    date_to=fields.Date(string="Fecha Final",required=True)
# 
#     period_id = fields.Many2one(
#             'account.period', 'Period',
#             help=_('Select period for your fiscal year'),
#             required=True
#         )
    target_move = fields.Selection(
            [('posted', 'All Posted Entries'),
             ('all', 'All Entries'), ],
            'Target Moves', required=True,default ='posted'
        )
    type_request = fields.Selection(
            [('AF', 'Control act'),
             ('FC', 'Certifying audit'),
             ('DE', 'Return'),
             ('CO', 'Write off')],
            'Type of request', required=True
        )
    order_num =fields.Char('Order number', size=13)
    pro_num = fields.Char('Procedure number', size=10)
    chart_account_id = fields.Many2one(
            'account.account', string='Filter on accounts',
            help="""Only selected accounts will be printed. Leave empty to
                    print all accounts."""
            )
# default = '_get_account_ids'

    def _check_order_num_old(self):
        res = self.read()[0]
        if res["order_num"] and res['type_request'] in ['AF', 'FC']:
            patron_order_num = re.compile(
                '[A-Z]{3}[0-6][0-9][0-9]{5}(/)[0-9]{2}'
            )
            match_order_num = patron_order_num.match(res["order_num"])
            if not match_order_num:
                return False
        return True

    def _check_pro_num_old(self):
        res = self.read()[0]
        if res["pro_num"] and res['type_request'] in ['DE', 'CO']:
            patron_pro_num = re.compile('[0-9]{10}')
            match_pro_num = patron_pro_num.match(res["pro_num"])
            if not match_pro_num:
                return False
        return True

#     _constraints = [
#         (_check_order_num,
#          'Order number not valid.\nVerify that the pattern is correct!',
#          ['order_num']),
#         (_check_pro_num,
#          'Procedure number not valid.\nVerify that the pattern is correct!',
#          ['pro_num']),
#     ]

    def validate_vat_old(self):
        # Validates that the company has VAT configured properly
        company_id = self.env['res.company']._company_default_get(object='account.print.chart.accounts.report')
        company = self.env['res.company'].browse(company_id).id

        vat_split = company.partner_id
        if not vat_split:
            raise ValidationError(
                _('Error'),
                _('Not found information for VAT of Company.\n'
                  'Verify that the configuration of VAT is correct!')
            )

    def change_company_id_old(self,company_id):
        """
        Update the period in the wizard based on the company id
        """
        res = {}
        period_id = self.env['date.range.type'].search([('company_id', '=', company_id)])
        if not period_id:
            raise ValidationError(
                _('Error'),
                _('Not found period for that Company.\n'
                  'Verify that the configuration of period is correct!')
            )
        return res

#     def change_fiscalyear_id(self,fiscalyear_id=False):
#         """
#         Update the period in the wizard based on the fiscal year
#         """
#         res = {}
#         res['value'] = {}
#         if fiscalyear_id:
#             period = False
#             self.enc.cr.execute('''
#                 SELECT * FROM (SELECT p.id
#                                FROM account_period p
#                                LEFT JOIN account_fiscalyear f ON
#                                (p.fiscalyear_id = f.id)
#                                WHERE f.id = %s
#                                ORDER BY p.date_start ASC
#                                LIMIT 1) AS period_start''' % fiscalyear_id)
#             periods = [i[0] for i in self.env.cr.fetchall()]
#             if periods and len(periods) > 0:
#                 period = periods[0]
#             res['value'] = {'period_id': period}
#         return res

    def build_report_name_old(self,data):
        """
        Builds the name of report
        """
#         from datetime import datetime
#         res = self.read()[0]
#         period_id = res['period_id'][0]
#         period_date = datetime.strptime(
#             self.env['account.period'].browse(period_id).date_stop, "%Y-%m-%d")
        company_id = self.env['res.company']._company_default_get(object='account.print.chart.accounts.report')
        company = self.env['res.company'].browse(company_id).id
        vat_split = company.partner_id

        report_name_sat = ''.join(
#             vat_split,
#             str(period_date.year),
#             str(period_date.month).rjust(2, '0'),
            'PL'
        )
        return report_name_sat
    ##############################################################
    def get_journal_entry_concept(self,move_id):
        """
        Get the concept of account journal entry based on the account move id
        concept of account journal entry is the account.move ref.
        """
        move_obj = self.env['account.move']
        concept = move_obj.browse(move_id).ref or "N/A"
        return concept

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

    def get_invoice_data(
        self,acc_move_line, journal_entry_type_xml,
        transaccion
    ):
        """
        Get the info of the Invoice based on the move_id of journal entry
        """
        invoice_obj = self.env['account.invoice']

        filters = []
        
        # if (
        #     journal_entry_type_xml in [1, 2] and
        #     (acc_move_line.get('reconcile_id') or
        #      acc_move_line.get('reconcile_partial_id'))
        # ):
        #     # if journal entry in Ingreso|Egreso
        #     reconcile_field = acc_move_line.get(
        #         'reconcile_id') and 'reconcile_id' or 'reconcile_partial_id'
        #     reconcile_value = acc_move_line.get(
        #         'reconcile_id') or acc_move_line.get('reconcile_partial_id')

        #     filters = [(reconcile_field, '=', reconcile_value),
        #                ('journal_id', '!=', acc_move_line.get('journal_id'))]

        #     move_obj = self.env['account.move.line']
        #     move_id = move_obj.search(filters)
        #     if move_id:
        #         move_data = move_obj.browse(move_id)

        #         for move in move_data:
        #             filters = [
        #                 ('move_id', '=', move.move_id.id),
        #                 ('account_id', '=', acc_move_line.get('account_id'))
        #             ]
        #     else:
        #         return False

        if journal_entry_type_xml in [3]:
            filters = [('move_id', '=', acc_move_line.get('move_id')),
                       ('account_id', '=', acc_move_line.get('account_id'))]
        else:
            return False

        invoice_id = invoice_obj.search(filters)
        invoice_data = invoice_obj.browse(invoice_id.ids)
        
        # Process each invoice if any
        for invoice in invoice_data:
            # Only add information about Comprobante
            # if there is an UUID at current invoice
            if invoice.cfdi_folio_fiscal:
                if not invoice.partner_id.vat_split:
                    raise ValidationError(
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
                    item_line.get('journal_id'),
                    item_line.get('account_id')
            ):
                journal_entry_type = self.get_journal_entry_type(
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

    def _get_lst_account(self):
        account_obj = self.env['account.account']
        actual_account = account_obj.search([]).ids
        #lst_account = []
        #self._fill_list_account_with_child(lst_account, actual_account)
        #raise ValidationError( str( lst_account))
        #raise ValidationError(  str( actual_account ))

        return tuple(actual_account)

    def _fill_list_account_with_child(self, lst_account, account):
        # no more child
        lst_account.append(account.id)
        if not account.child_id:
            return
        for child in account.child_id:
            self._fill_list_account_with_child(lst_account, child)

    @api.multi
    def generate_report(self, data):
        context = self.env.context
        import tempfile
        
        account_move_model = self.env['account.move']

        Etree = ET.ElementTree()
        # #Begin of Sql query Section
        #period_id = data["form"]["period_id"]
        target_move = self.target_move
        #period_obj = self.env['account.period']
        #period = period_obj.browse(
        #    period_id,
        #    context=self.actual_context
        #)
        
        sql_select = """
        SELECT al.debit,al.credit,al.amount_currency,al.date,al.journal_id,
        al.ref,al.move_id,al.name,al.currency_id,al.account_id,al.reconciled
        FROM account_move_line al """
        sql_where = """
        WHERE al.date >=  %(date)s
        AND al.date <=  %(date_to)s 
        AND al.account_id in %(account_id)s """
        search_params = {
            'date': self.date_from,
            'date_to': self.date_to,
            'account_id': self._get_lst_account()
        }
       

        sql_joins = ''
        sql_orderby = 'ORDER BY al.move_id'
        if target_move == 'posted':
            sql_joins = 'LEFT JOIN account_move am ON move_id = am.id '
            sql_where += """ AND am.state = %(target_move)s"""
            search_params.update({'target_move': target_move})
        query_sql = ' '.join((sql_select, sql_joins, sql_where, sql_orderby))


        
        self.env.cr.execute(query_sql, search_params)
        lines = self.env.cr.dictfetchall()
        
        # #End of Sql query Section
        if not lines:
            raise ValidationError(
                _('Error'),
                _('Not found Journal Entries for this Period.\n'
                  'Choose another Period!')
            )
        # if Journal Entries have lines will create the xml report
        # Create main journal entries node
        type_request =self.type_request
        order_num = self.order_num
        pro_num = self.pro_num
        from datetime import datetime
        time_period = datetime.strptime(self.date_from, "%Y-%m-%d")

        polizas = ET.Element('PLZ:Polizas')
        # namespace
        polizas.set("xsi:schemaLocation",
                    "www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo/PolizasPeriodo_1_1.xsd")
        polizas.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        polizas.set("xmlns:PLZ", "www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo")

        polizas.set('Version', '1.1')
        polizas.set('RFC', 'vat_split')
        polizas.set('Mes', str(time_period.month).rjust(2, '0'))
        polizas.set('Anio', str(time_period.year))
        polizas.set('TipoSolicitud', type_request)
        if order_num:
            polizas.set('NumOrden', order_num)
        if pro_num:
            polizas.set('NumTramite', pro_num)


        Etree._setroot(polizas)

        # Groups of account move based on move id,
        # each group is one journal entrie
        from collections import defaultdict
        groups = defaultdict(list)
        for line in lines:
            groups[line.get('move_id')].append(line)

        
        for move_id in groups.keys():
            # Load account.move object for current move lines
            move = account_move_model.browse(
                move_id
            )
            cumul_debit = 0.0
            cumul_credit = 0.0
            poliza = ET.SubElement(polizas, 'PLZ:Poliza')
            
            

            # Check for SAT journal type using
            journal_entry_type_xml = self.get_journal_entrie_type_xml(
                 groups[move_id]
            )
            

            for item_line in groups[move_id]:
                # required fields on journal entry node
                cumul_debit += item_line.get('debit') or 0.0
                cumul_credit += item_line.get('credit') or 0.0
                journal_id = item_line.get('journal_id')
                # #Begin on transaction node
                trans_concept = item_line.get('name')
                acccta = self.get_trans_cta(
                   item_line.get('account_id')
                )
                transaccion = ET.SubElement(poliza, 'PLZ:Transaccion')
                transaccion.set("NumCta", acccta.code)#acccta.code)
                transaccion.set("DesCta", acccta.name)#acccta.name)
                transaccion.set("Concepto", (trans_concept).encode(
                    'utf-8', 'ignore').decode('utf-8')
                )
                transaccion.set("Debe", str(item_line.get('debit')))
                transaccion.set("Haber", str(item_line.get('credit')))
                

                


                # Begin on journal entry node
                if journal_entry_type_xml in [2]:
                    # Get the check data related to the journal entry move
                    ##########comeptado por acccta
                    self.get_check_data( move_id, journal_id,
                       acccta.id, transaccion
                    )
                    # #End of Check section
                # # Begin for Invoice CFDI Section

                self.get_invoice_data( item_line, journal_entry_type_xml,
                    transaccion
                )
                
                # # End for Invoice CFDI Section

                # Get the Transferencia or otrMetodoPago data related for the Journal Entry move
                if journal_entry_type_xml in [1, 2]:
                    self.get_transferencia_data(
                        item_line, journal_entry_type_xml,
                        transaccion
                    )

                    self.get_otr_metodo_pago(
                        item_line, journal_entry_type_xml,
                        transaccion
                    )
                #raise ValidationError( str( self ))
                # # End of Transferencia Section
                # #End on transaction node
            journal_entry_concept = self.get_journal_entry_concept( move_id
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
        #raise ValidationError( str( report.name ))
        return report.name


    @api.multi
    def print_report(self):
        #return self.env.ref('l10n_mx_eaccounting.journal_entries_print_report').report_action(self)
        
#         self.validate_vat()
#         report_name = self.build_report_name(data)
        data= {
#             "period_id": res["period_id"].id,
            "account_id": self.chart_account_id,
            "target_move": self.target_move,
            'type_request': self.type_request,
            'order_num': self.order_num,
            'pro_num':self.pro_num,
        }
        file=self.generate_report(data)
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?data='+str(file)+'&filename=hola.xml',
            'target': 'self'}
        #raise ValidationError( str( data ))
# 
#         return {
#             'type': 'ir.actions.report.xml',
#             'report_name': 'journal.entries.xml',
#             'datas': data,
#             'name': report_name,
#             'context': {
#                 'FileExt': 'xml',
#                 'compress': True,
#                 'FileName': report_name
#             }
#         }
