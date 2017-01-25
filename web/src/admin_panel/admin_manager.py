from flask_admin_impexp.admin_impexp import AdminImportExport

from src import admin, db
from src.user.models import User, UserProfile, Role, Permission, UserRole
from src.user.schemas import UserProfileSchema, UserSchema, UserRoleSchema


class MyModel(AdminImportExport):
    pass

admin.add_view(MyModel(User, session=db.session, schema=UserSchema))
admin.add_view(MyModel(UserProfile, session=db.session, schema=UserProfileSchema))
admin.add_view(MyModel(Role, session=db.session))
admin.add_view(MyModel(UserRole, session=db.session, schema=UserRoleSchema))
admin.add_view(MyModel(Permission, session=db.session))
