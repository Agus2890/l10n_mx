# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Creacion de Factura Electronica para Mexico (CFD)',
    'version': '2.0.',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
This module creates e-invoice files from
invoices with standard CFD-2010 of Mexican SAT.

Requires the following programs:

xsltproc
    Ubuntu insall with:
        sudo apt-get install xsltproc

openssl
    Ubuntu insall with:
        sudo apt-get install openssl
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'l10n_mx_facturae_groups',
        'account',
        'base_vat',
        # 'document',
        # 'report_webkit',
        'l10n_mx_facturae_lib',
        'l10n_mx_facturae_cer',
        'l10n_mx_account_tax_category',
        # 'l10n_mx_company_cif',
        # 'l10n_mx_partner_address',
        'l10n_mx_invoice_amount_to_text',
        'l10n_mx_ir_attachment_facturae',
        # 'l10n_mx_notes_invoice',
        # 'l10n_mx_res_partner_bank',
        'l10n_mx_regimen_fiscal',
        'l10n_mx_company_multi_address',
        'l10n_mx_base_vat_split',
        'l10n_mx_facturae_group_show_wizards',
        'l10n_mx_payment_method',
        'l10n_mx_catalogs'
    ],
    'demo': [
    ],
    'data': [
        # 'data/l10n_mx_facturae_report_header.xml',
        # 'data/l10n_mx_facturae_report.xml',
        # 'wizard/installer_view.xml',
        'views/account_move_view.xml',
        'report/report_move_cfdi.xml',
        'report/facturae_report.xml',
        'report/report_move_cfdi_sin_logo.xml',
    ],
    'installable': True,
}
