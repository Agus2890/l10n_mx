from odoo import models, http, api
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
import base64

class Binary(http.Controller):

    @http.route('/web/binary/download_document', type='http', auth="public")
    @serialize_exception
    def download_document(self,data,filename=None, **kw):
        #Model = request.registry[model]
        #cr, uid, context = request.cr, request.uid, request.context
        #fields = [field]
        #res = Model.read(cr, uid, [int(id)], fields, context)[0]
        file=open(data,'rb').read()
        gentextfile =str(base64.b64encode(file),encoding='utf-8')
        file_decode=base64.b64decode(gentextfile)

        filecontent = file_decode#res.get(field)
        headers = [
            ('Content-Type', 'application/zip'),
            ('Content-Disposition', content_disposition(filename)),
            ('charset', 'utf-8'),
        ]
        return request.make_response(
                filecontent, headers=headers, cookies=None)


