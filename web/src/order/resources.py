from .schemas import Order, OrderSchema, Invoice, InvoiceSchema

from src.utils import ModelResource, operators as ops, AssociationModelResource
from .. import db
from ..user.models import Partner


class OrderResource(ModelResource):

    model = Order
    schema = OrderSchema

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class InvoiceResource(ModelResource):

    model = Invoice
    schema = InvoiceSchema

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):

        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True

    def after_objects_update(self, objects) -> None:
        for obj in objects:
            total = 0
            print(obj)
            for i in obj.inline_items:
                print(i)
                i.invoice_id = obj.id
                i.total = i.quantity * i.price
                if i.pro_rata:
                    i.total = (i.days / 30) * float(i.total)
                total += float(i.total)
                print(i.total)
            tax = 0.09
            if obj.type == 'from' and Partner.query.filter(Partner.id == obj.partner_id).with_entities(Partner.gst_type).limit(
                    1).scalar() == 'unregistered':
                tax = 0
            obj.sgst = total * tax
            obj.cgst = total * tax
            obj.sub_total = total
            obj.total = obj.sub_total + obj.sgst + obj.cgst
            db.session.commit()
            print(obj.sub_total, obj.sgst, obj.cgst)