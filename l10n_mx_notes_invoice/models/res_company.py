# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _


class ResCompany(models.Model):
    _inherit = 'res.company'

    dinamic_text = fields.Text('Promissory note', translate=True,
            help='This text will put in the report of Invoice')
    dict_var = fields.Text('Variables to use in text',
            help='Put te variables used in text')
    sample_text = fields.Text('Promissory note', readonly=True,
        defaults="'I %(partner_name)s pay to the order of %(company_"\
            "name)s the amount of %(invoice_amount)s'")
    sample_dict = fields.Text('Variables to use in text', readonly=True,
        defaults="'partner_name' : partner.name, 'company_name' : "\
            "company.name, 'invoice_amount' : invoice.amount_total")
    details = fields.Text('Variables to use in text', readonly=True,
        defaults="In the field 'Promissory note' you need put the text "\
            "that you like that was colocate in the report as promissory, if "\
            "you like take a data from the parner, company or the invoice "\
            "you need create a new variable in the field 'Variables to use "\
            "in text' as follows : \n'name_variable' : object.value of object, "\
            "and when you need use an variable you put %(variable)s for use "\
            "information from an object. \nWhen you need information from "\
            "the partner, use partner.field that you need from the partner, "\
            "for company use company.field an equal for an field from invoice.")
    sample = fields.Text('Variables to use in text', readonly=True,
        defaults='If you like put the text \nI Partner pay to the order of '\
            'My Company the amount of $500.00, you need put:')

