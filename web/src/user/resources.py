from flask_login import current_user

from src.utils import ModelResource, operators as ops
from .models import User, Partner, PosOutlet
from .schemas import UserSchema, PartnerSchema, PosOutletSchema


class UserResource(ModelResource):
    model = User
    schema = UserSchema

    auth_required = True

    filters = {
        'username': [ops.Equal, ops.Contains],
        'active': [ops.Boolean]
    }

    order_by = ['email', 'id']

    only = ()

    exclude = ()

    def has_read_permission(self, qs):
        return qs.filter(User.id == current_user.id)

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class PosOutletResource(ModelResource):
    model = PosOutlet
    schema = PosOutletSchema

    auth_required = True

    filters = {
        'username': [ops.Equal, ops.Contains],
        'active': [ops.Boolean]
    }

    order_by = ['email', 'id']

    only = ()

    exclude = ()

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class PartnerResource(ModelResource):
    model = Partner
    schema = PartnerSchema

    auth_required = True

    filters = {
        'username': [ops.Equal, ops.Contains],
        'active': [ops.Boolean],
        'type': [ops.Equal, ops.Contains]
    }

    order_by = ['email', 'id']

    only = ()

    exclude = ()

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True
