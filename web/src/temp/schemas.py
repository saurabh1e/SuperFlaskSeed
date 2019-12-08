from src import ma, BaseSchema
from .models import Order, InlineItem, Transfer


class OrderSchema(BaseSchema):

    class Meta:
        model = Order

    id = ma.Integer()
    transaction_id = ma.Integer()
    admin_id = ma.Integer()
    vendor_id = ma.Integer()

    roles = ma.Nested('RoleSchema', many=True)


class InlineItemSchema(BaseSchema):

    class Meta:
        model = InlineItem

    id = ma.Integer()
    name = ma.String(required=True)
    unique_id = ma.Integer(unique=True)
    order_id = ma.Integer()
    transfer_id = ma.Integer()


class TransferSchema(BaseSchema):

    class Meta:
        model = Transfer

    id = ma.Integer()
    amount = ma.Integer()
    admin_id = ma.Integer()
    client_id = ma.Integer()

    roles = ma.Nested('RoleSchema', many=True)
