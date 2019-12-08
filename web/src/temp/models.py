from flask_security import RoleMixin, UserMixin
from sqlalchemy import UniqueConstraint

from src import db, BaseMixin, ReprMixin


class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    inline_items = db.relationship('InlineItem', back_populates='order', uselist=True, lazy='dynamic')

    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    admin_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    vendor_id = db.Column(db.ForeignKey('user.id'), nullable=False)

    admin = db.relationship('AdminRole', backref='order', foreign_keys=[admin_id])
    vendor = db.relationship('VendorRole', backref='order', foreign_keys=[vendor_id])


class InlineItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    unique_id = db.Column(db.String(64), nullable=False, unique=True)
    order_id = db.Column(db.ForeignKey('order.id'), nullable=False, back_populates='inline_items')
    transfer_id = db.Column(db.ForeignKey('transfer.id'), nullable=False, back_populates='inline_items')


class Transfer(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    admin_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.ForeignKey('user.id'), nullable=False)

    inline_items = db.relationship('InlineItem', uselist=True, lazy='dynamic')
    admin = db.relationship('AdminRole', backref='order', foreign_keys=[admin_id])
    client = db.relationship('VendorRole', backref='order', foreign_keys=[client_id])
