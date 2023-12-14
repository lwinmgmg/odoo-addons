from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class ShopPaymentOrderConfirm(WebsiteSale):

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, sale_order_id=None, **post):
        res = super().shop_payment_validate(sale_order_id, **post)

        if sale_order_id is None and not 'sale_last_order_id' in request.session:
            return res
        order = request.env['sale.order'].sudo().browse(sale_order_id or request.session['sale_last_order_id'])
        order.action_confirm()

        return res
