from sqlalchemy.dialects.postgresql import NUMERIC, ENUM
from sqlalchemy.ext.hybrid import hybrid_property

from src import db, BaseMixin, ReprMixin


class Order(BaseMixin, db.Model, ReprMixin):
    pos_outlet_id = db.Column(db.ForeignKey('pos_outlet.id'), nullable=False)
    posify_id = db.Column(db.String(100), nullable=False, unique=True)
    sub_total = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    discount = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    tax = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    other_charges = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    total = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    outlet_name = db.Column(db.String(100), nullable=False)
    outlet_identity = db.Column(db.String(100), nullable=False)

    brand_commission_value = db.Column(NUMERIC(4, 2), nullable=False, default=0)
    brand_commission_total = db.Column(NUMERIC(4, 2), nullable=False, default=0)

    kitchen_commission_value = db.Column(NUMERIC(4, 2), nullable=False, default=0)
    kitchen_commission_total = db.Column(NUMERIC(4, 2), nullable=False, default=0)

    pos_outlet = db.relationship('PosOutlet', foreign_keys=[pos_outlet_id])


class Invoice(BaseMixin, db.Model, ReprMixin):
    partner_id = db.Column(db.ForeignKey('partner.id'), nullable=False)
    type = db.Column(ENUM('to', 'from', name='invoice_type'), default='to')
    sub_total = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    total_tax = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    total = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    from_date = db.Column(db.Date(), nullable=True)
    to_date = db.Column(db.Date(), nullable=True)
    sgst = db.Column(NUMERIC(8, 2), default=0, nullable=True)
    cgst = db.Column(NUMERIC(8, 2), default=0, nullable=True)
    igst = db.Column(NUMERIC(8, 2), default=0, nullable=True)

    partner = db.relationship('Partner', foreign_keys=[partner_id])
    inline_items = db.relationship('InlineItem', uselist=True, lazy='dynamic', back_populates='invoice', cascade='all, delete-orphan',)

    @hybrid_property
    def partner_name(self):
        return self.partner.name


class InlineItem(BaseMixin, db.Model, ReprMixin):

    item = db.Column(db.String(100), nullable=False)
    quantity = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    price = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    total = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    pro_rata = db.Column(db.Boolean(), default=False)
    days = db.Column(db.SmallInteger(), default=0)
    description = db.Column(db.String(300), nullable=True)

    invoice_id = db.Column(db.ForeignKey('invoice.id'), nullable=True)

    # taxes = db.relationship('InlineItemTax', uselist=True)
    invoice = db.relationship('Invoice', foreign_keys=[invoice_id], back_populates='inline_items',  )


class InlineItemTax(BaseMixin, db.Model, ReprMixin):
    tax = db.Column(db.String(100), nullable=False)
    value = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    amount = db.Column(NUMERIC(8, 2), default=0, nullable=False)

    # inline_item_id = db.Column(db.ForeignKey('inline_item.id'), nullable=False)

    # inline_item = db.relationship('InlineItem', foreign_keys=[inline_item_id])