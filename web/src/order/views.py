import json

from flask import request, make_response

from src.utils import BaseView, AssociationView
from .models import Order
from .resources import OrderResource, InvoiceResource
from src import api, bp, db
from ..user.models import PosOutlet


@api.register()
class OrderView(BaseView):

    @classmethod
    def get_resource(cls):
        return OrderResource


@api.register()
class InvoiceView(BaseView):

    @classmethod
    def get_resource(cls):
        return InvoiceResource


@bp.route('/pos/order', methods=['POST'])
def get_payment_info():
    data = request.json
    print(json.dumps(data))
    o = Order()
    pos_outlet_id = PosOutlet.query.filter(PosOutlet.posify_id == data['order']['store']['id']).with_entities(PosOutlet.id).limit(1).scalar()
    o.pos_outlet_id = pos_outlet_id
    o.created_on = data['order']['details']['datetime']
    o.posify_id = data['order']['details']['id']
    o.sub_total = data['order']['details']['order_subtotal']
    o.discount = data['order']['details']['discount']
    o.tax = data['order']['details']['total_tax']
    o.total = data['order']['details']['order_total']
    o.outlet_name = data['order']['store']['name']
    o.outlet_identity = data['order']['store']['identity']

    o.brand_commission_value = 0
    o.brand_commission_total = 0

    o.kitchen_commission_value = 0
    o.kitchen_commission_total = 0

    db.session.add(o)
    db.session.commit()

    return make_response('', 200)
