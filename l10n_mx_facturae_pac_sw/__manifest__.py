# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": """
        Creacion de Factura Electronica para Mexico (CFDI 3.3-2019)
        - PAC SW Sapien
    """,
    "version": "1.0",
    'author': 'Mikrointeracciones',
    "category": "Localization/Mexico",
    "description": """
    This module creates interface for
    e-invoice files from invoices with SW sapien.
Ubuntu Package Depends:
    sudo apt-get install python-soappy
""",
    'website': 'http://www.mikrointeracciones.com.mx',
    "license": "AGPL-3",
    "depends": [
        "l10n_mx_facturae_groups",
        "l10n_mx_params_pac",
        # "l10n_mx_account_tax_category",
        "l10n_mx_ir_attachment_facturae",
        "l10n_mx_facturae_pac",
        "l10n_mx_facturae_group_show_wizards",
        # "l10n_mx_facturae_validate_cfdi",
        # "account_cancel",
        "l10n_mx_payment_cfdi"
    ],
    "demo": [],
    
    "installable": True,
    "active": False,
}
