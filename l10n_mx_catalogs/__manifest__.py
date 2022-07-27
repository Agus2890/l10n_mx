# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Catalogs CFDI Facturae 3.3',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description' : """
This module extends to Facturae 3.3 of Localization/México
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'depends': [
        'base',
        'account',
        'product',
        'sale',
    ],    
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/catalog_view.xml',
        'views/product_view.xml',
        'views/account_move_view.xml',
        'wizard/account_invoice_refund_view.xml',
        #'data/l10n_mx_product.xml',
        #'data/l10n_mx_product_units.xml',
        'data/l10n_mx_usocfdi.xml'
        ],
    'active': False,
    'installable': True,
}
