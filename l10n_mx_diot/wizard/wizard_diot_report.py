# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from io import StringIO, BytesIO
#from io import BytesIO
import io
import base64

import logging
from odoo.exceptions import UserError
from odoo.tools import mute_logger, pycompat
_logger = logging.getLogger(__name__)


class WizardAccountDiotMX(models.TransientModel):
    _name = 'account.diot.report'
    _description = 'Account - Mexico DIOT Report'


    name = fields.Char('File Name', size=25, readonly=True)
    # company_id = fields.Many2one('res.company', 'Company', required=True, select=True)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.diot.report'))
    # period_id = fields.Many2one('account.period', 'Period',help=_('Select period for your report'), required=True)
    filename = fields.Char('Filename', size=128, readonly=True, help='This is File name')
    file = fields.Binary('File', readonly=True, help='This file, you can import the SAT')
    filename_xls = fields.Char('Filename', size=128, readonly=True, help='This is File name')
    file_xls = fields.Binary('File', readonly=True, help='This file, you can import the SAT')
    state = fields.Selection([('choose', 'Choose'),('get', 'Get'),('not_file', 'Not File')], default='choose')
    target_move = fields.Selection([('posted', 'All Posted Entries'), ('all', 'All Entries')], 'Target Moves', default='posted', required=True)
    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Date range'
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.model
    def default_get(self,fields):
        """
        This function load in the wizard, the company used by the user, and
        the previous period to the current
        """
        import datetime
        from dateutil.relativedelta import relativedelta

        print ("-------------------------- fields ---------------------------",fields)

        # comp = self.env['res.company']
        comp = self._context.get('company_id', self.env.user.company_id.id)
        data = super(WizardAccountDiotMX, self).default_get(fields)
        time_now = datetime.date.today() + relativedelta(months=-1)
        # company_id = comp#._company_default_get('account.diot.report')
        _logger.info("Fields------------>: %s " % (self)) 
        # period_id = self.env['account.period'].search(
        #     [('date_start', '<=', time_now),
        #      ('date_stop', '>=', time_now),
        #      ('company_id', '=', company_id)]
        # )
        # if period_id:
        #     data.update({'company_id': company_id,
        #                 'period_id': period_id[0]})
        return data

    def create_report(self):
        """
        This function is used when click on button
        and call function that properly create report
        """
        this = self#.browse()
        res, state = self._calculate_diot()
        period = this.date_range_id
        _logger.info("Company create report ------------>: %s " % (this.company_id.name)) 
        if state == 'partners':
            return {
                'name': _('This suppliers do not have the information'
                          ' necessary for the DIOT report'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'type': 'ir.actions.act_window',
                'domain': [
                    ('id', 'in', res),
                    '|', ('active', '=', False), ('active', '=', True)
                ],
            }
        # There are some lines with out partner ask user to fix them
        if state == 'lines':
            return {
                'name': _('This lines do not have partner and cannot be '
                          'processed for Diot report'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', res)],
            }
        # There are some lines with partner market as not vat subjected
        if state == 'vat_subjected':
            return {
                'name': _('Lines assigned to a partner not vat subjected.'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', res)],
            }
        # Select state for redraw the form
        if len(res):
            state = 'get'
            name = "%s-%s-%s.txt" % ("DIOT", this.company_id.name, period.name)
            name_xls = "%s-%s-%s.xls" % ("DIOT", this.company_id.name, period.name)
            # Write record
            self.write({
                'state': state,
                'file': base64.b64encode(self._get_csv(res).encode()),
                'filename': name,
                'file_xls':base64.b64encode(self._get_xls(res)),
                'filename_xls': name_xls
                })
        else:
            state = 'not_file'
            self.write({'state': state})

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'res_model': 'account.diot.report',
            'target': 'new',
        }

    def _calculate_diot(self):
        """
        This function create the file for report to DIOT, take the amount base
        paid by partner in each tax, in the period and company selected.
        old_field tax2_id = tar_line_id and tax2_base = tax_base_amount
        new_field
        """

        # Validate tax configuration
        tax_obj = self.env['account.tax']
        tax_ids = tax_obj.search(
            [('tax_category_id', '!=', False), ('type_tax_use', '=', 'purchase')])
            # [('tax_categ', '=', 'vat'), ('type_tax_use', '=', 'purchase')])
        # Variable for get all the account_ids to use on the report
        acc_ids = []
        # for tax in tax_obj.browse(tax_ids):
        for tax in tax_ids:
            if not tax.diot_group or not tax.cash_basis_account:
                raise UserError(
                    _('Error!' 'Tax %s is not configured correctly' % tax.name)
                )
            else:
                acc_ids.append(tax.cash_basis_account.id)

        # Get data to filter account move lines for report
        this = self#.browse()
        company = this.company_id
        period = this.date_range_id
        # _logger.debug("Selecting period %s" % period.name)
        state = this.target_move

        # Get lines to analyze on report
        acm_line_obj = self.env['account.move.line']


        acml_ids = acm_line_obj.search(
            [('company_id', '=', company.id),
             # ('period_id', '=', period.id),
             ('date', '<=', this.date_to),
             ('date', '>=', this.date_from),
             ('account_id', 'in', acc_ids),
             # ('tax2_id', 'in', tax_ids),
             # ('tax2_id', 'in', tax_ids.ids),
             ('tax_line_id', 'in', tax_ids.ids),
             ],)
        # raise UserError(
        #             _('Error!' 'ACML ids %s' % acml_ids)
        #         )
        # Init analysis
        suppliers = {}
        fix_lines = []
        review_lines = []
        # for acml in acm_line_obj.browse(acml_ids):
        for acml in acml_ids:    
            # Filter move lines according to account.move
            # status selected by user on wizard and by
            # use_in_diot flag
            if (
                (state == 'posted' and acml.move_id.state != 'posted')
                # or not acml.move_id.use_in_diot
            ):
                continue
            
            # raise UserError(
            #         _('Error!' 'ACML for %s' % acml)
            #     )

            if not acml.partner_id:
                fix_lines.append(acml.id)
                continue
            # if not acml.partner_id.vat_subjected:
            if acml.partner_id.country_id.code != 'MX':    
                review_lines.append(acml.id)
                continue
            supplier = suppliers.setdefault(
                acml.partner_id.id,
                {'base_16': 0,
                 'base_11': 0,
                 'base_0': 0,
                 'base_ex': 0,
                 'ret_vat': 0
                 })
            # Get partner data so we don't need to browse it again
            supplier['partner'] = acml.partner_id
            # Adding tax base according to proper tax
            if acml.tax_line_id.diot_group == 'vat_16':
                supplier['base_16'] += abs(acml.tax_base_amount)
            elif acml.tax_line_id.diot_group == 'vat_11':
                supplier['base_11'] += abs(acml.tax_base_amount)
            elif acml.tax_line_id.diot_group == 'vat_0':
                supplier['base_0'] += abs(acml.tax_base_amount)
            elif acml.tax_line_id.diot_group == 'no_vat':
                supplier['base_ex'] += abs(acml.tax_base_amount)
            # Add VAT retentions if present
            # if acml.tax_ret:
            #     supplier['ret_vat'] += abs(acml.tax_ret)
        # Return special response to indicate that there are lines
        # to fix in order to properly create the report
        if fix_lines:
            return fix_lines, 'lines'
        # Return special response to indicate that there are lines
        # to review to ensure data is correct for create the report
        if review_lines:
            return review_lines, 'vat_subjected'

        # Init response
        from .constants import CODES
        res = []
        fix_partners = []
        for supplier_id in suppliers:
            supplier = suppliers[supplier_id]['partner']
            data = suppliers[supplier_id]
            # Validate DIOT information on partner form
            if (
                not supplier.vat_split or not supplier.type_of_third
                or not supplier.type_of_operation
                or (supplier.type_of_third == '05' and not supplier.country_id)
            ):
                fix_partners.append(supplier.id)
                continue

            _logger.debug("Adding supplier %s to report" % supplier.name)
            code = (supplier.country_id.code
                    if supplier.country_id.code in CODES else 'XX')
            res.append({
                'h1': supplier.type_of_third,
                'h2': supplier.type_of_operation,
                'h3': (supplier.vat_split if supplier.type_of_third == '04' else ''),

                'h4': (supplier.vat_split if supplier.type_of_third == '05' else ''),
                'h5': (supplier.name.encode('utf-8') if supplier.type_of_third == '05' else ''),
                'h6': code if supplier.type_of_third == '05' else '',
                'h7': (supplier.nacionality_diot
                       if supplier.type_of_third == '05' else ''),
                'h8': ("%.0f" % data['base_16'] if 'base_16' in data and
                       data['base_16'] > 0 else ''),
                'h9': '',
                'h10': '',
                'h11': ("%.0f" % data['base_11'] if 'base_11' in data and
                        data['base_11'] > 0 else ''),
                'h12': '',
                'h13': '',
                'h14': '',
                'h15': '',
                'h16': '',
                'h17': '',
                'h18': '',
                'h19': ("%.0f" % data['base_0'] if 'base_0' in data and
                        data['base_0'] > 0 else ''),
                'h20': ("%.0f" % data['base_ex'] if 'base_ex' in data and
                        data['base_ex'] > 0 else ''),
                'h21': ("%.0f" % data['ret_vat'] if 'ret_vat' in data and
                        data['ret_vat'] > 0 else ''),
                'h22': '',
            })
        # Return special response for display list of partners
        # to fix for report
        if fix_partners:
            return fix_partners, 'partners'
        # Return response with data for create report
        return res, True

    def _get_csv(self, lines, delimiter='|'):
        #from io import BytesIO
        """
        Generates a txt file for import into SAT Diot program
        """
        import csv
        import tempfile

        names = [
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'h7',
            'h8',
            'h9',
            'h10',
            'h11',
            'h12',
            'h13',
            'h14',
            'h15',
            'h16',
            'h17',
            'h18',
            'h19',
            'h20',
            'h21',
            'h22',
            'h23'  # We needed to add an extra column to force delimeter
        ]
        with tempfile.NamedTemporaryFile(delete=False,suffix='.csv') as f:
            with open(f.name, mode='w') as fcsv:
                csvwriter = csv.DictWriter(
                    fcsv, delimiter=delimiter, fieldnames=names
                )
                for line in lines:
                    csvwriter.writerow( line)

        with open(f.name, 'r') as fname:
            data = fname.read()
        return data

      
    def _get_xls(self, lines):
        #raise UserError(  str( lines ))
        """
        Generates an excel file for review DIOT results
        """
        import tempfile
        from xlwt import Workbook

        book = Workbook(encoding='utf-8')
        sheet = book.add_sheet('DIOT')
        # Write head for sheet
        from .constants import HEADERS
        for cell in range(1, 22):
            sheet.write(0, cell - 1, HEADERS['h' + str(cell)])
        # Write data into sheet
        count = 1
        for line in lines:
            for cell in range(1, 22):
                try:
                    t = float(line['h' + str(cell)])
                except:
                    t = line['h' + str(cell)  ]
            
                sheet.write(count, cell - 1, str(t))

            count += 1
        ###file_data=StringIO.StringIO()
        file_data=BytesIO()
        book.save(file_data)
        data= file_data.getvalue() 
        # Write data into file
        # with tempfile.NamedTemporaryFile(delete=False,suffix='.xls') as fcsv:
        #     book.save(fcsv.name)

        # with open(fcsv.name, 'r') as fname:
        #     data = fname.read()

        
        return data