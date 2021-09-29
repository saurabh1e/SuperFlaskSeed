from flask_admin_impexp.admin_impexp import AdminImportExport

from src import admin, db
from src.user.models import User, Role, Permission, UserRole, Partner, PosOutlet, Address
from src.order.models import Order, Invoice, InlineItem, InlineItemTax
from src.user.schemas import UserSchema, UserRoleSchema

class MyModel(AdminImportExport):
    pass

class PartnerAdmin(AdminImportExport):
    inline_models = (Address,)
    pass


admin.add_view(MyModel(User, session=db.session, schema=UserSchema))
admin.add_view(MyModel(Role, session=db.session))
admin.add_view(PartnerAdmin(Partner, session=db.session))
admin.add_view(MyModel(PosOutlet, session=db.session))
admin.add_view(MyModel(Address, session=db.session))
admin.add_view(MyModel(Order, session=db.session))
admin.add_view(MyModel(UserRole, session=db.session, schema=UserRoleSchema))
admin.add_view(MyModel(Permission, session=db.session))
admin.add_view(MyModel(Invoice, session=db.session))
admin.add_view(MyModel(InlineItem, session=db.session))
admin.add_view(MyModel(InlineItemTax, session=db.session))
