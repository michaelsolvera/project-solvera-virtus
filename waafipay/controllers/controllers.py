# -*- coding: utf-8 -*-
from odoo import http
import logging
import pprint
import hashlib
from datetime import datetime

import requests
import werkzeug
from werkzeug import urls

from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
_logger = logging.getLogger(__name__)



class WebsiteSaleInherit(WebsiteSale):
    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public",
                website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        # Ensure a payment acquirer is selected
        request.env.context = dict(request.env.context)
        request.env.context.update({"waafipay_payment_type": request.params.get("waafipay_payment_type")})
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()

        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return False

        assert order.partner_id.id != request.website.partner_id.id

        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)

        transaction = order._create_payment_transaction(vals)

        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        return transaction.with_context(wafi_payment_type=request.params.get("waafipay_payment_type")).render_sale_button(order)

class PaymentProcessing(PaymentProcessing):

    @staticmethod
    def add_payment_transaction(transactions):
        if not transactions:
            return False
        tx_ids_list = set(request.session.get("__payment_tx_ids__", [])) | set(transactions.ids)
        request.session["__payment_tx_ids__"] = list(tx_ids_list)
        return True


class Waafipay(http.Controller):
    _return_url = '/handle_waafipay_response'

    # @http.route('/shop/payment/token', type='http', auth="public", methods=['POST', 'GET'], csrf=False)
    # def waafipay_dpn_gavdhjs(self, **post):
    #     print("yes")

    @http.route('/handle_waafipay_response', type='http', auth="public", methods=['POST', 'GET'], csrf=False)
    def waafipay_dpn(self, **post):
        """ waafipay DPN """
        _logger.info('Beginning waafipay DPN form_feedback with post data %s', pprint.pformat(post))  # debug
        try:
            print("Confirmation Done.")
            res = self.waafipay_validate_data(**post)
        except ValidationError:
            _logger.exception('Unable to validate the waafipay payment')
        return werkzeug.utils.redirect('/payment/process')

    def waafipay_validate_data(self, **post):
        response = self.get_hpp_resultinfo(post)
        res = False
        # post['cmd'] = '_notify-validate'
        reference = response.json()["params"]["referenceId"]
        tx = None
        if reference:
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', reference.split("'")[1].replace("/","-"))])
        if not tx:
            # we have seemingly received a notification for a payment that did not come from
            # odoo, acknowledge it otherwise paypal will keep trying
            _logger.warning('received notification for unknown payment reference')
            return False

        resp = []
        if tx:
            resp.append(response.json()['params']['state'])
        else:
            resp.append(response.json()['params']['state'])
        if 'APPROVED' in resp:
            _logger.info('WaafiPay: validated data')
            res = request.env['payment.transaction'].sudo().form_feedback(response, 'waafipay')
            if not res and tx:
                tx._set_transaction_error('Validation error occured. Please contact your administrator.')
        elif 'DECLINED' in resp:
            _logger.warning('WaafiPay: answered INVALID/FAIL on data verification')
            if tx:
                tx._set_transaction_error('Invalid response from WaafiPay. Please contact your administrator.')
        else:
            _logger.warning(
                'WaafiPay: unrecognized paypal answer, received %s instead of VERIFIED/SUCCESS or INVALID/FAIL (validation: %s)' % (
                resp, 'PDT' if pdt_request else 'IPN/DPN'))
            if tx:
                tx._set_transaction_error('Unrecognized error from WaafiPay. Please contact your administrator.')
        return res

    def get_hpp_resultinfo(self, post):
        import requests
        key = request.env['payment.acquirer'].sudo().search([('provider', '=', "waafipay")]).waafipay_storekey
        storeid = request.env['payment.acquirer'].sudo().search([('provider', '=', "waafipay")]).waafipay_storeid
        merchantid = request.env['payment.acquirer'].sudo().search([('provider', '=', "waafipay")]).waafipay_merchant_id

        url = "https://sandbox.safarifoneict.com/asm"

        payload = "{\n            \"schemaVersion\"     : \"1.0\"," \
                  "\n            \"requestId\"         : \"R17100517154423\"," \
                  "\n            \"timestamp\"         : \"%s\"," \
                  "\n            \"channelName\"       : \"WEB\"," \
                  "\n            \"serviceName\"       : \"HPP_GETRESULTINFO\"," \
                  "\n\n            \"serviceParams\"     : {" \
                  "\n\n                \"storeId\"       : \"%s\"," \
                  "\n                \"hppKey\"        : \"%s\"," \
                  "\n                \"merchantUid\"   : \"%s\"," \
                  "\n                \"hppResultToken\": \"%s\"\n}" \
                  "\n}" % (datetime.now(), storeid, key, merchantid, post['hppResultToken'])
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        return response
