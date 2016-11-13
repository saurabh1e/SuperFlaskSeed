from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from flask_user import UserMixin
from flask_security import RoleMixin
from sqlalchemy import UniqueConstraint

from src import db, BaseMixin, ReprMixin


class UserRole(db.Model, BaseMixin):

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

    user = db.relationship('User', back_populates='roles')
    role = db.relationship('Role', back_populates='users')

    UniqueConstraint(user_id, role_id)


class Role(db.Model, RoleMixin, ReprMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    users = db.relationship('UserRole', back_populates='role')


class User(db.Model, BaseMixin, UserMixin, ReprMixin):
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
    roles = db.relationship('UserRole', back_populates='user')

    user_profile = db.relationship("UserProfile", uselist=False, back_populates="user", cascade='all, delete-orphan')

    @hybrid_property
    def name(self):
        if self.user_profile and self.user_profile.first_name:
            if self.user_profile.last_name:
                return self.user_profile.first_name + self.user_profile.last_name
            return self.user_profile.first_name


class UserProfile(db.Model, BaseMixin):
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.Enum('male', 'female', 'na'), default='na')
    dob = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    profile_picture = db.Column(db.Text(), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)

    user = db.relationship('User', back_populates="user_profile", single_parent=True)

    @hybrid_property
    def age(self):
        if self.dob:
            return datetime.now().year - self.dob.year
        else:
            return 0


class PermissionSet(db.Model, BaseMixin, ReprMixin):

    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

