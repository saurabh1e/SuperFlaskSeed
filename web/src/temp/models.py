from flask_security import RoleMixin, UserMixin
from sqlalchemy import UniqueConstraint

from src import db, BaseMixin, ReprMixin


class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)

    inline_items = db.relationship('InlineItem', backref='order')
    admin = db.relationship('AdminRole', backref='order')
    vendor = db.relationship('VendorRole', backref='order')


class InlineItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey(Order.id), nullable=False)


class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    orders = db.relationship('Order', backref='transaction')


class AdminRole(BaseMixin, db.Model):

    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))

    user = db.relationship('User', foreign_keys=[admin_id])
    role = db.relationship('Role', foreign_keys=[role_id])


class VendorRole(BaseMixin, db.Model):

    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))

    user = db.relationship('User', foreign_keys=[vendor_id])
    role = db.relationship('Role', foreign_keys=[role_id])


class CustomerRole(BaseMixin, db.Model):

    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))

    user = db.relationship('User', foreign_keys=[customer_id])
    role = db.relationship('Role', foreign_keys=[role_id])
