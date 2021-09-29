from flask_security import RoleMixin, UserMixin
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, NUMERIC

from src import db, ReprMixin, BaseMixin


class UserPermission(ReprMixin, BaseMixin, db.Model):

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    permission_id = db.Column(db.Integer(), db.ForeignKey('permission.id', ondelete='CASCADE'))

    user = db.relationship('User', foreign_keys=[user_id])
    permission = db.relationship('Permission', foreign_keys=[permission_id])

    UniqueConstraint(user_id, permission_id)


class UserRole(ReprMixin, BaseMixin, db.Model):

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

    user = db.relationship('User', foreign_keys=[user_id])
    role = db.relationship('Role', foreign_keys=[role_id])

    UniqueConstraint(user_id, role_id)


class Role(ReprMixin, BaseMixin, db.Model, RoleMixin):
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    users = db.relationship('User', back_populates='roles', secondary='user_role')


class User(ReprMixin, BaseMixin, db.Model, UserMixin):
    email = db.Column(db.String(127), unique=True, nullable=False)
    password = db.Column(db.String(255), default='', nullable=False)
    username = db.Column(db.String(127), nullable=True)

    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())

    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', back_populates='users', secondary='user_role')
    permissions = db.relationship('Permission', back_populates='users', secondary='user_permission')

    def has_permission(self, permission):
        if isinstance(permission, str):
            return permission in (permission.name for permission in self.permissions)
        else:
            return permission in self.permissions


class Permission(ReprMixin, BaseMixin, db.Model):

    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    users = db.relationship('User', back_populates='permissions', secondary='user_permission')


class Partner(ReprMixin, BaseMixin, db.Model):

    __repr_fields__ = ('id', 'name')

    name = db.Column(db.String(80), unique=True)
    code = db.Column(db.String(80), unique=True)
    name_2 = db.Column(db.String(80), unique=True)

    phone = db.Column(db.String(80), unique=True)
    type = db.Column(ENUM('brand', 'kitchen', name='partner'), nullable=False)
    gst_type = db.Column(ENUM('consumer', 'registered', 'unregistered', name='registered'), nullable=False)
    gst_number = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(128), nullable=True)

    mg = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    electricity_rate = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    electricity_type = db.Column(ENUM('per_unit', 'fixed', default='fixed'), nullable=False)
    fixed_fee = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    address = db.relationship('Address', single_parent=False)
    commissions = db.relationship('CommissionSlab', single_parent=False, uselist=True)


class CommissionSlab(ReprMixin, BaseMixin, db.Model):
    partner_id = db.Column(db.ForeignKey('partner.id'))
    partner = db.relationship('Partner', foreign_keys=[partner_id])
    amount = db.Column(NUMERIC(8, 2), default=0, nullable=False)
    value = db.Column(NUMERIC(4, 2), default=0, nullable=False)
    slab_type = db.Column(ENUM('fixed', 'percentage', name='slab_type'), default='percentage')


class Address(ReprMixin, BaseMixin, db.Model):
    line_1 = db.Column(db.String(80), unique=True)
    line_2 = db.Column(db.String(80), unique=True)
    city = db.Column(db.String(80), unique=True)
    state = db.Column(db.String(80), unique=True)
    pin_code = db.Column(db.String(80), unique=True)

    partner_id = db.Column(db.ForeignKey('partner.id'))
    partner = db.relationship('Partner', foreign_keys=[partner_id])


class PosOutlet(ReprMixin, BaseMixin, db.Model):

    name = db.Column(db.String(50), nullable=False)
    identity = db.Column(db.String(50), nullable=False)
    brand_partner_id = db.Column(db.ForeignKey('partner.id'), nullable=False)
    kitchen_partner_id = db.Column(db.ForeignKey('partner.id'), nullable=False)
    created_on = db.Column(db.TIMESTAMP(), )
    disabled_on = db.Column(db.TIMESTAMP(), )
    posify_id = db.Column(db.String(64), nullable=False)
    kitchen_partner = db.relationship('Partner', foreign_keys=[kitchen_partner_id], uselist=False)
    brand_partner = db.relationship('Partner', foreign_keys=[brand_partner_id], uselist=False)
