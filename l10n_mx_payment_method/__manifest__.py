# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MX Payment Method',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/Mexico',
    'description': """
MX Paymet Method
================

Add 'Payment Method' to partner and invoice, it's used by l10n_mx_facturae
module and 'acc_payment' to invoice
    """,
    'website': 'http://www.mikrointeracciones.com.mx',    
    'license': 'AGPL-3',
    'depends': [
        "sale",
        'account',
        'l10n_mx_catalogs',
    ],
    'demo': [
    ],
    'data': [
        'security/rules.xml',
        'security/ir.model.access.csv',        
        'views/payment_type_view.xml',
        'views/account_payment_view.xml',
        'views/account_move_view.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'data/payment_method_data.xml',        
    ],
    'installable': True,
    'active': False,
}
