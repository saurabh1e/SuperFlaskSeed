from src import ma, BaseSchema
from .models import Order, Invoice, InlineItem, InlineItemTax


class OrderSchema(BaseSchema):

    class Meta:
        model = Order
        exclude = ('created_on', 'updated_on')

    id = ma.Integer(dump_only=True)


class InvoiceSchema(BaseSchema):

    class Meta:
        model = Invoice
        exclude = ('created_on', 'updated_on')

    id = ma.Integer(dump_only=True)
    inline_items = ma.Nested('InlineItemSchema', many=True, load=True)
    partner_name = ma.String(dump_only=True)
    sub_total = ma.Float(dump_only=True)
    total = ma.Float(dump_only=True)
    sgst = ma.Float(dump_only=True)
    cgst = ma.Float(dump_only=True)


class InlineItemSchema(BaseSchema):

    class Meta:
        model = InlineItem
        exclude = ('created_on', 'updated_on')

    id = ma.Integer(dump_only=True)
    taxes = ma.Nested('InlineItemTaxSchema', many=True, load=True)
    total = ma.Float(dump_only=True)
    invoice_id = ma.Integer(load=False, dump=True)


class InlineItemTaxSchema(BaseSchema):

    class Meta:
        model = InlineItemTax
        exclude = ('created_on', 'updated_on')

    id = ma.Integer(dump_only=True)