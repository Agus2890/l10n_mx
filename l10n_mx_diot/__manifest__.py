# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'DIOT Report',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
DIOT Report
===========

Create DIOT Report for Mexico
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'depends': [
        'l10n_mx_base_vat_split',
        'l10n_mx_account_tax_category',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/account_move_view.xml',
        'views/account_tax_view.xml',
        'wizard/wizard_diot_report_view.xml',
    ],
    'installable': True,
    'active': False,
}
