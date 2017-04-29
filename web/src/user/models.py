from flask_security import RoleMixin, UserMixin
from sqlalchemy import UniqueConstraint

from src import db, BaseMixin, ReprMixin


class UserPermission(BaseMixin, db.Model):

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    permission_id = db.Column(db.Integer(), db.ForeignKey('permission.id', ondelete='CASCADE'))

    user = db.relationship('User', foreign_keys=[user_id])
    permission = db.relationship('Permission', foreign_keys=[permission_id])

    UniqueConstraint(user_id, permission_id)


class UserRole(BaseMixin, db.Model):

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

    user = db.relationship('User', foreign_keys=[user_id])
    role = db.relationship('Role', foreign_keys=[role_id])

    UniqueConstraint(user_id, role_id)


class Role(BaseMixin, db.Model, RoleMixin, ReprMixin):
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    users = db.relationship('User', back_populates='roles', secondary='user_role')


class User(BaseMixin, db.Model, UserMixin, ReprMixin):
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

    user_profile = db.relationship("UserProfile", uselist=False, back_populates="user",
                                   cascade='all, delete-orphan', lazy='subquery')

    def has_permission(self, permission):
        if isinstance(permission, str):
            return permission in (permission.name for permission in self.permissions)
        else:
            return permission in self.permissions


class UserProfile(BaseMixin, db.Model):
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.Enum('male', 'female', 'na', name='gender'), default='na')
    dob = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    profile_picture = db.Column(db.Text(), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)

    user = db.relationship('User', back_populates="user_profile", single_parent=True)


class Permission(BaseMixin, db.Model, ReprMixin):

    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    users = db.relationship('User', back_populates='permissions', secondary='user_permission')
