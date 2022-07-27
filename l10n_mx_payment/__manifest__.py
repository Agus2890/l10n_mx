# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Payment Accounting Mx',
    'version': '14.0.1.0',
    'author': 'Mikrointeracciones de México',
    'website': 'http://www.mikrointeracciones.com.mx',
    'summary': 'Account Mexican',
    'description' : """
This module extends the payment accounting functionality according to the Mexican location
    """,
    'depends': [
        'account',
        'l10n_mx',
    ],
    'category': 'Account',
    'sequence': 10,
    'demo': [],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_payment_view.xml',
    ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
