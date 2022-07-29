# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Receipt Payments CFDI 3.3',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description' : """
Payment stamp
===========

This module allows you to stamp payments related to invoices
    """,
    'website': 'http://www.mikrointeracciones.com.mx',    
    'depends': [
        'account',
        'l10n_mx_ir_attachment_facturae',
        'l10n_mx_facturae_groups',
        # 'l10n_mx_payment',
    ],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        # 'data/l10n_mx_payment_mail_templates_data.xml',            
        'views/ir_attachment_payment_view.xml',
        'views/account_payment_view.xml',
        'report/payment_report.xml',
        'report/report_payment_template.xml',        
    ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
