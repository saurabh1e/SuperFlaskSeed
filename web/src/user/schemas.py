from src import ma, BaseSchema
from .models import User, Role, Permission, UserRole, PosOutlet, Partner, Address, CommissionSlab


class UserSchema(BaseSchema):

    class Meta:
        model = User
        exclude = ('created_on', 'updated_on', 'password', 'current_login_at', 'current_login_ip',
                   'last_login_at', 'last_login_ip', 'login_count', 'confirmed_at')

    id = ma.Integer(dump_only=True)
    email = ma.Email(unique=True, primary_key=True, required=True)
    username = ma.String(required=True)
    roles = ma.Nested('RoleSchema', many=True, dump_only=True)


class RoleSchema(BaseSchema):

    class Meta:
        model = Role
        exclude = ('users',)
    name = ma.String()


class UserRoleSchema(BaseSchema):

    class Meta:
        model = UserRole

    id = ma.Integer(load=True)
    user_id = ma.Integer(load=True)
    role_id = ma.Integer(load=True)
    user = ma.Nested('UserSchema', many=False)
    role = ma.Nested('RoleSchema', many=False)


class PermissionSchema(BaseSchema):

    class Meta:
        model = Permission
        exclude = ('users',)


class PosOutletSchema(BaseSchema):

    class Meta:
        model = PosOutlet

    kitchen_partner_id = ma.Integer(load=True, dump=True)
    brand_partner_id = ma.Integer(load=True, dump=True)


class PartnerSchema(BaseSchema):

    class Meta:
        model = Partner

    address = ma.Nested('AddressSchema', dump_only=True)
    commissions = ma.Nested('CommissionSlabSchema', many=True, load=True)


class AddressSchema(BaseSchema):

    class Meta:
        model = Address


class CommissionSlabSchema(BaseSchema):
    class Meta:
        model = CommissionSlab
