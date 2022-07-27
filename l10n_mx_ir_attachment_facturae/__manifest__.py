# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Creacion de Attachment en la Factura Electronica para Mexico (CFD,CFDI,CBB)',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
This module creates attachment for Invoice(CFD,CFDI,CBB)
    """,
    'website': 'www.mikrointeracciones.com.mx', 
    'license': 'AGPL-3',
    'depends': [
        'account',
        'mail',
        # 'email_template',
    ],
    'demo': [
        'demo/l10n_mx_facturae_email_demo.xml',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_attachment_facturae_view.xml',
        'views/account_move_view.xml',  
        # 'data/l10n_mx_facturae_mail_server_data.xml',
        # 'data/l10n_mx_facturae_mail_templates_data.xml',
        # 'views/res_config.xml',
        'views/account_journal_view.xml',  
    ],
    'installable': True,
    'active': False,
}
