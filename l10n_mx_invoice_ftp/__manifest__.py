# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Attachment of invoice to FTP',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/Mexico',
    'description' : """This module supports attachment of invoice to ftp""",
    'website': 'www.mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends' : [
        'l10n_mx_facturae',
        'l10n_mx_upload_ftp',
    ],
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : ['wizard/wizard_facturae_ftp_view.xml'],
    'installable' : True,
    'active' : False,
}
