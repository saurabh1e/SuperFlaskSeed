from flask import render_template
from flask_security import login_required, current_user
from flask_admin.contrib import sqla

from src import admin, db
from src.user.models import User, UserProfile, Role, PermissionSet, UserRole

@login_required
def index():
    return render_template('index.html')


class MyModel(sqla.ModelView):
    column_display_pk = True

    def is_accessible(self):
        return current_user.has_role('admin')


admin.add_view(MyModel(User, session=db.session))
admin.add_view(MyModel(UserProfile, session=db.session))
admin.add_view(MyModel(Role, session=db.session))
admin.add_view(MyModel(UserRole, session=db.session))
admin.add_view(MyModel(PermissionSet, session=db.session))
