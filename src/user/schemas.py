from src import ma, BaseSchema
from .models import UserProfile, User, Role, PermissionSet, UserRole


class UserSchema(BaseSchema):

    class Meta:
        model = User
        exclude = ('created_on', 'updated_on', 'password', 'current_login_at', 'current_login_ip',
                   'last_login_at', 'last_login_ip', 'login_count')

    id = ma.Integer(dump_only=True)
    email = ma.Email(unique=True, primary_key=True, required=True)
    username = ma.String(required=True)
    user_profile = ma.Nested('UserProfileSchema', load=True, many=False, exclude=('user',))
    roles = ma.Nested('RoleSchema', many=True, dump_only=True)


class UserProfileSchema(BaseSchema):

    class Meta:
        model = UserProfile
        exclude = ('created_on', 'updated_on')

    id = ma.Integer(dump_only=True)
    first_name = ma.String(load=True)
    user = ma.Nested('UserSchema', load=False)


class RoleSchema(BaseSchema):

    class Meta:
        model = Role
        exclude = ('users',)


class UserRoleSchema(BaseSchema):

    class Meta:
        model = UserRole
        exclude = ('users', 'roles')

    user_id = ma.Integer(load=True)
    role_id = ma.Integer(load=True)


class PermissionSetSchema(BaseSchema):

    class Meta:
        model = PermissionSet
        exclude = ('users',)

