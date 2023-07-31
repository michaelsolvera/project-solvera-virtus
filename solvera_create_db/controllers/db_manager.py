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
    @http.route('/web/login/daftar', type='http', auth='public', website=True)
    def index(self, **kw):
        return http.request.render('solvera_create_db.index')

    @http.route('/web/berhasil', type='http', auth='public', website=True)
    def create_contact(self, **post):

        DATABASE = post.get('username')
        # SERVER = 'http://localhost:8999'
        SERVER = 'https://solvy.id/'
        CLIENT = 'https://app.solvy.id/'
        ##admin password bawaan erppeek
        ADMIN_PASSWORD = 'admin'
        NAME=post.get('name')
        LOGIN=post.get('email')
        PASSWORD=post.get('pw')
        phone=post.get('phone')
        packet = post.get('packet')
        now = datetime.now()
        passsword= request.env['']


        client = erppeek.Client(server=SERVER)
        app = erppeek.Client(server=CLIENT)
        login = erppeek.Client(server=SERVER,db='solvy',user='admin',password='&g%$raNY9]_VGE5,')
        # login = erppeek.Client(server=SERVER,db='testing_sign_up',user='admin',password='1')

        
        print(packet,'coba1')
        if not DATABASE in app.db.list():
            login.login('admin', '&g%$raNY9]_VGE5,', 'solvy')
     
            partner_dict={
                'name':NAME,
                'mobile':phone,
                'email':LOGIN,
                'packet':packet,
                'db':DATABASE,
                'pw':PASSWORD,
                'time_request':now,
                }
            create_res_partner=login.model('res.partner').create(partner_dict)

        else:
            values = request.params.copy()
            values['error'] = _("Nama Perusahaan Telah Digunakan")
            response = request.render('solvera_create_db.index', values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        
        partner_obj=login.model('res.partner').search([('db','=',DATABASE)])
       
        strings = [str(integer) for integer in partner_obj]
        a_string = "".join(strings)
        an_integer = int(a_string)
        agrs=(partner_obj,an_integer)
        print(an_integer,'strtoint')
        # login.write('res.partner',partner_obj,member_dict)
        login.execute_kw('res.partner','send_email',agrs,())
        login.execute_kw('res.partner','get_token',agrs,())
        
            
        return http.request.redirect('/web/email_sent')
    @http.route('/web/create_db', type='http', auth='public', website=True)
    def create_db(self, **post):

        DATABASE = post.get('username')
        # SERVER = 'http://localhost:8999'
        SERVER = 'https://solvy.id/'
        CLIENT = 'https://app.solvy.id/'
        ADMIN_PASSWORD = 'admin'
        NAME=post.get('name')
        LOGIN=post.get('login')
        PASSWORD=post.get('pw')
        phone=post.get('phone')
        packet = post.get('packet')
        now = datetime.now()
        exp = now+ timedelta(days=60)

        app = erppeek.Client(server=CLIENT)
        client = erppeek.Client(server=SERVER)
        login = erppeek.Client(server=SERVER,db='solvy',user='admin',password='&g%$raNY9]_VGE5,')
        # admin = erppeek.Client(server=SERVER,db=DATABASE,user='admin',password='admin')
        print(packet,'packet')
        if not DATABASE in app.db.list():
            if packet == '1':
                
                #targetclone db
                app.login('admin', '&g%$raNY9]_VGE5,', 'solvy-lite-master')
                app.clone_database('bimn-my2u-qskb', DATABASE)
                app.login('admin','&g%$raNY9]_VGE5,',DATABASE)
                app.model('res.users').create({
                    'login': LOGIN,
                    'name':NAME,
                    'password':PASSWORD,
                    })

                login.login('admin','&g%$raNY9]_VGE5,','solvy')
                partner_obj=login.model('res.partner').search([('db','=',DATABASE)])

                value={
                    'time_verification':now,
                    'exp_date':exp,
                    # 'member_lines':data_member,
                }

                login.write('res.partner',partner_obj,value)

            if packet == '2':

                #targetclone db
                app.login('admin', '&g%$raNY9]_VGE5,', 'solvy-lite-master')
                app.clone_database('bimn-my2u-qskb', DATABASE)
                app.login('admin','&g%$raNY9]_VGE5,',DATABASE)
                app.model('res.users').create({
                    'login': LOGIN,
                    'name':NAME,
                    'password':PASSWORD,
                    })

                login.login('admin','&g%$raNY9]_VGE5,','solvy')
                partner_obj=login.model('res.partner').search([('db','=',DATABASE)])

                value={
                    'time_verification':now,
                    'exp_date':exp,
                    # 'member_lines':data_member,
                }

                login.write('res.partner',partner_obj,value)
            if packet == '3':

                #targetclone db
                app.login('admin', '&g%$raNY9]_VGE5,', 'solvy-lite-master')
                app.clone_database('bimn-my2u-qskb', DATABASE)
                app.login('admin','&g%$raNY9]_VGE5,',DATABASE)
                app.model('res.users').create({
                    'login': LOGIN,
                    'name':NAME,
                    'password':PASSWORD,
                    })

                login.login('admin','&g%$raNY9]_VGE5,','solvy')
                partner_obj=login.model('res.partner').search([('db','=',DATABASE)])

                value={
                    'time_verification':now,
                    'exp_date':exp,
                    # 'member_lines':data_member,
                }

                login.write('res.partner',partner_obj,value)
            return http.request.redirect('https://app.solvy.id/web?db='+DATABASE)
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

    @http.route('/web/email_sent', type='http', auth='public', website=True)
    def email_sent(self, **kw):
        return http.request.render('solvera_create_db.email_sent')
        
        

    @http.route('/web/login/user', type='http', auth='public', website=True)
    def user(self, **kw):
        return http.request.render('solvera_create_db.user')


    @http.route('/web/login/userlogin', type='http', auth='public', website=True)
    def userlogin(self,redirect = None, *kw ,**post):
        ##servernya pakai solvy
        # SERVER = 'http://localhost:8999'
        CLIENT = 'https://app.solvy.id/'
        SERVER = 'https://solvy.id'
        PASSWORD=post.get('password')
        DB=post.get('username')
        USER=post.get('email')

        app = erppeek.Client(server=CLIENT)
        if DB in app.db.list():
            return http.request.redirect('https://app.solvy.id/web?db='+post.get('username'))
        else:
            values = request.params.copy()
            values['error'] = _("Nama Company Tidak Tersedia")
            response = request.render('solvera_create_db.user', values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response


    @http.route('/web/lupa_password', type='http', auth='public', website=True)
    def forgot_password(self, **kw):
        return http.request.render('solvera_create_db.lupa_password') 

    @http.route('/web/check_user', type='http', auth='public', website=True)
    def check_user(self, *kw ,**post):
        EMAIL = post.get('email')
        # SERVER = 'http://localhost:8999'
        COMPANY = post.get('username')
        SERVER = 'https://solvy.id'
        CLIENT = 'https://app.solvy.id/'

        login = erppeek.Client(server=SERVER,db='solvy',user='admin',password='&g%$raNY9]_VGE5,')
        client = erppeek.Client(server=SERVER)
        app = erppeek.Client(server=CLIENT)

        login.login('admin','&g%$raNY9]_VGE5,','solvy')
        partner_obj=login.model('res.partner').search([('email','=',EMAIL),('db','=',COMPANY)])
        print(partner_obj,'partnertest')
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
            response = request.render('solvera_create_db.lupa_password', values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response

    @http.route('/web/email_sent_reset', type='http', auth='public', website=True)
    def email_sent_reset(self, *kw ,**post):
        return http.request.render('solvera_create_db.email_sent_reset')

    @http.route('/web/change_password', type='http', auth='public', website=True)
    def change_password(self, *kw ,**post):
        DATABASE = post.get('username')
        # SERVER = 'http://localhost:8999'
        SERVER = 'https://solvy.id/'
        NAME=post.get('name')
        LOGIN=post.get('email')
        token=post.get('token')

        return http.request.render('solvera_create_db.new_password',{
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
            # login.write('res.partner',partner_obj,member_dict)
            login_solvy.execute_kw('res.partner','get_token',agrs,())

            return http.request.redirect('/web/login/user')    
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

            
    ###callback from controller
    @http.route('/web/callback_xendit', type='http', auth='public', website=True)
    def callback_xendit(self, **post):
        
        EMAIL = post.get('payer_email')
        STATUS = post.get('status')
        ID = post.get('id')
        COMPANY = post.get('username')
        SERVER = 'https://solvy.id/'
        CLIENT = 'https://app.solvy.id/'

        login = erppeek.Client(server=SERVER,db='solvy',user='admin',password='&g%$raNY9]_VGE5,')
        client = erppeek.Client(server=SERVER)
        app = erppeek.Client(server=CLIENT)

        login.login('admin','&g%$raNY9]_VGE5,','solvy')
        partner_obj=login.model('res.partner').search([('email','=',EMAIL),('invoice_id','=',ID)])
        if partner_obj :
            strings = [str(integer) for integer in partner_obj]
            a_string = "".join(strings)
            an_integer = int(a_string)
            agrs=(partner_obj,an_integer)
            login.execute_kw('res.partner','paid',agrs,())
            return http.request.render('solvera_create_db.payment_success')

    @http.route('/web/db_lock', type='http', auth='public', website=True)
    def db_lock(self, **post):
        

        db = post.get('db')
        SERVER = 'https://solvy.id/'
        CLIENT = 'https://app.solvy.id/'

        login = erppeek.Client(server=SERVER,db='solvy',user='admin',password='&g%$raNY9]_VGE5,')
        client = erppeek.Client(server=SERVER)
        app = erppeek.Client(server=CLIENT)

        client.login('admin','&g%$raNY9]_VGE5,',db)
        user_obj=client.model('res.company').search([('partner_id','!=',False)])
        value={
            'is_hide_all_menu':True,
        }
        client.write('res.company',user_obj,value)
        if user_obj :
            strings = [str(integer) for integer in user_obj]
            a_string = "".join(strings)
            an_integer = int(a_string)
            agrs=(user_obj,an_integer)
            client.execute_kw('res.company','expired',agrs,())

    @http.route('/web/db_unlock', type='http', auth='public', website=True)
    def db_unlock(self, **post):
        

        db = post.get('db')
        SERVER = 'https://solvy.id/'
        CLIENT = 'https://app.solvy.id/'

        login = erppeek.Client(server=SERVER,db='solvy',user='admin',password='&g%$raNY9]_VGE5,')
        client = erppeek.Client(server=SERVER)
        app = erppeek.Client(server=CLIENT)

        client.login('admin','&g%$raNY9]_VGE5,',db)
        user_obj=client.model('res.company').search([('partner_id','!=',False)])
        value={
            'is_hide_all_menu':False,
        }
        client.write('res.company',user_obj,value)
        if user_obj :
            strings = [str(integer) for integer in user_obj]
            a_string = "".join(strings)
            an_integer = int(a_string)
            agrs=(user_obj,an_integer)
            client.execute_kw('res.company','expired',agrs,())
