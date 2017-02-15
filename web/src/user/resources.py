from .schemas import User, UserProfile, UserSchema, UserProfileSchema, Role, RoleSchema, UserRole, UserRoleSchema

from src.utils import ModelResource, operators as ops, AssociationModelResource


class UserProfileResource(ModelResource):

    model = UserProfile
    schema = UserProfileSchema

    def has_read_permission(self, request, qs):
        return qs

    def has_change_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):
        if not obj.user_id:
            obj.user_id = 1
        return True


class RoleResource(ModelResource):
    model = Role
    schema = RoleSchema

    def has_read_permission(self, request, qs):
        return qs

    def has_change_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):
        if not obj.user_id:
            obj.user_id = 1
        return True


class UserRoleResource(AssociationModelResource):

    model = UserRole
    schema = UserRoleSchema

    def has_read_permission(self, request, qs):
        return qs

    def has_change_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):
        if not obj.user_id:
            obj.user_id = 1
        return True


class UserResource(ModelResource):

    model = User
    schema = UserSchema

    filters = {
        'username': [ops.Equal, ops.Contains],
        'active': [ops.Boolean]
    }

    related_resource = {
        'user_profile': UserProfileResource
    }

    order_by = ['email', 'id']

    only = ()

    exclude = ()

    def has_read_permission(self, request, qs):
        return qs

    def has_change_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):

        return True
