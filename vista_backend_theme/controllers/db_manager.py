
import json
import requests

from tempfile import mkstemp
import erppeek




from shutil import move
from odoo.exceptions import UserError
import werkzeug.wrappers

import odoo
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_module_path, get_resource_path
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo.tools.safe_eval import safe_eval, time
from odoo import http, tools,_,fields
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security
from datetime import datetime,timedelta




class WebsitePendaftaran(http.Controller):


    @http.route('/web/lupa_password', type='http', auth='public', website=True)
    def forgot_password(self, **kw):
        return http.request.render('vista_backend_theme.lupa_password') 

    @http.route('/web/check_user', type='http', auth='public', website=True)
    def check_user(self, *kw ,**post):
        EMAIL = post.get('email')
        # SERVER = 'http://localhost:8999'
        COMPANY = post.get('username')
        SERVER = 'https://solvy.id'

        login = erppeek.Client(server=SERVER,db='solvy',user='admin',password='&g%$raNY9]_VGE5,')
        client = erppeek.Client(server=SERVER)

        login.login('admin','&g%$raNY9]_VGE5,','solvy')
        partner_obj=login.model('res.partner').search([('email','=',EMAIL),('db','=',COMPANY)])
        if partner_obj :
            strings = [str(integer) for integer in partner_obj]
            a_string = "".join(strings)
            an_integer = int(a_string)
            agrs=(partner_obj,an_integer)
            login.execute_kw('res.partner','send_change_password',agrs,())
            return http.request.redirect('/web/email_sent_reset')

        else:
            values = request.params.copy()
            values['error'] = _("Email Tidak Tersedia")
            response = request.render('vista_backend_theme.lupa_password', values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response

    @http.route('/web/email_sent_reset', type='http', auth='public', website=True)
    def email_sent_reset(self, *kw ,**post):
        return http.request.render('vista_backend_theme.email_sent_reset')

    @http.route('/web/change_password', type='http', auth='public', website=True)
    def change_password(self, *kw ,**post):
        DATABASE = post.get('username')
        # SERVER = 'http://localhost:8999'
        SERVER = 'https://solvy.id/'
        NAME=post.get('name')
        LOGIN=post.get('email')
        token=post.get('token')

        return http.request.render('vista_backend_theme.new_password',{
            'name': NAME,
            'username':DATABASE,
            'login':LOGIN,
            'token': token,


        })

    @http.route('/web/set_newpassword', type='http', auth='public', website=True)
    def set_newpassword(self, *kw ,**post):
        DATABASE = post.get('username')
        # SERVER = 'http://localhost:8999'
        SERVER = 'https://solvy.id/'
        CLIENT = 'https://app.solvy.id/'
        NAME=post.get('name')
        password=post.get('pw')
        TOKEN=post.get('token')

        login = erppeek.Client(server=CLIENT,db=DATABASE,user='admin',password='&g%$raNY9]_VGE5,')
        login_solvy = erppeek.Client(server=SERVER,db='solvy',user='admin',password='&g%$raNY9]_VGE5,')

        login_solvy.login('admin','&g%$raNY9]_VGE5,','solvy')
        token_obj=login_solvy.model('res.partner').search([('token','=',TOKEN)])

        if token_obj:
            login.login('admin','&g%$raNY9]_VGE5,',DATABASE)
            user_obj=login.model('res.users').search([('name','=',NAME)])
            value={
                'password':password,
            }
            login.write('res.users',user_obj,value)

            login_solvy.login('admin','&g%$raNY9]_VGE5,','solvy')
            partner_obj=login_solvy.model('res.partner').search([('name','=',NAME)])
        
            strings = [str(integer) for integer in partner_obj]
            a_string = "".join(strings)
            an_integer = int(a_string)
            agrs=(partner_obj,an_integer)
            print(an_integer,'strtoint')
            login_solvy.execute_kw('res.partner','get_token',agrs,())

            return http.request.redirect('/web/login')    
        else:
            return werkzeug.wrappers.Response(
                status = 400,
                content_type='aplication/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin','*')],
                response=json.dumps({
                    'error': 'Error',
                    'error_description': 'Error'
                })
            
            )