# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Validación de Facturas CFDI',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
This module validates electronic invoices
through webservice of mexican SAT
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'l10n_mx_facturae',
        'l10n_mx_payment_cfdi'
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
    ],
    'installable': True,
}
