from werkzeug.utils import secure_filename
import csv

from flask_admin._compat import csv_encode
from flask import flash, request, redirect, Response, stream_with_context
from flask_admin.base import expose
from flask_admin.babel import gettext
from sqlalchemy.exc import OperationalError, IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import UnmappedInstanceError
from flask_admin.helpers import get_redirect_target
from flask import render_template
from flask_security import login_required, current_user
from flask_admin.contrib import sqla
import flask_excel as excel

from src import admin, db
from src.user.models import User, UserProfile, Role, PermissionSet, UserRole
from src.user.schemas import UserProfileSchema, UserSchema, UserRoleSchema


def product_init(data, schema, model):
    for d in data:
        if d['id'] is not None and not d['id'] == '':
            obj, errors = schema().load(d, instance=model.query.get(d['id']))
        else:
            obj, errors = schema().load(d, session=db.session)
        if errors:
            flash(str(errors), 'error')
            db.session.rollback()
            raise InvalidRequestError
        try:
            if not obj.id:
                db.session.add(obj)
            db.session.commit()
        except(InvalidRequestError, IntegrityError, UnmappedInstanceError, OperationalError) as e:
            raise e


class MyModel(sqla.ModelView):
    column_display_pk = True
    column_filters = ('id',)
    can_export = True
    list_template = 'list_template.html'

    def __init__(self, model, session, schema=None):
        self.schema = schema
        super(MyModel, self).__init__(model, session)

    @expose('/export/<export_type>/')
    def export(self, export_type):

        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_export or (export_type not in self.export_types):
            flash(gettext('Permission denied.'), 'error')
            return redirect(return_url)

        if export_type == 'csv':
            return self._export_csv(return_url)

    def _export_csv(self, return_url):
        count, data = self._export_data()

        # https://docs.djangoproject.com/en/1.8/howto/outputting-csv/
        class Echo(object):
            """
            An object that implements just the write method of the file-like
            interface.
            """

            def write(self, value):
                """
                Write the value by returning it, instead of storing
                in a buffer.
                """
                return value

        writer = csv.writer(Echo())

        def generate():
            # Append the column titles at the beginning
            titles = [i.name for i in self.model.__table__.columns]
            yield writer.writerow(titles)

            for row in data:
                vals = [csv_encode(getattr(row, c))
                        for c in titles]
                yield writer.writerow(vals)

        filename = self.get_export_name(export_type='csv')

        disposition = 'attachment;filename=%s' % (secure_filename(filename),)

        return Response(
            stream_with_context(generate()),
            headers={'Content-Disposition': disposition},
            mimetype='text/csv'
        )

    @expose('/import', methods=['POST'])
    def import_excel(self):

        try:
            if self.schema:
                data = request.get_records(field_name='files')
                product_init(data, self.schema, model=self.model)
                db.session.commit()
        except (InvalidRequestError, IntegrityError, UnmappedInstanceError, OperationalError) as e:
            flash(str(e), 'error')
            db.session.rollback()

        return redirect(self.url)

    def is_accessible(self):
        return current_user.has_role('admin')


class MyModel(sqla.ModelView):
    column_display_pk = True
    column_filters = ('id',)
    can_export = True
    list_template = 'list_template.html'

    def __init__(self, model, session, schema=None):
        self.schema = schema
        super(MyModel, self).__init__(model, session)

    @expose('/export/<export_type>/')
    def export(self, export_type):

        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_export or (export_type not in self.export_types):
            flash(gettext('Permission denied.'), 'error')
            return redirect(return_url)

        if export_type == 'csv':
            return self._export_csv(return_url)

    def _export_csv(self, return_url):
        count, data = self._export_data()

        # https://docs.djangoproject.com/en/1.8/howto/outputting-csv/
        class Echo(object):
            """
            An object that implements just the write method of the file-like
            interface.
            """

            def write(self, value):
                """
                Write the value by returning it, instead of storing
                in a buffer.
                """
                return value

        writer = csv.writer(Echo())

        def generate():
            # Append the column titles at the beginning
            titles = [i.name for i in self.model.__table__.columns]
            yield writer.writerow(titles)

            for row in data:
                vals = [csv_encode(getattr(row, c))
                        for c in titles]
                yield writer.writerow(vals)

        filename = self.get_export_name(export_type='csv')

        disposition = 'attachment;filename=%s' % (secure_filename(filename),)

        return Response(
            stream_with_context(generate()),
            headers={'Content-Disposition': disposition},
            mimetype='text/csv'
        )

    @expose('/import', methods=['POST'])
    def import_excel(self):

        try:
            if self.schema:
                data = request.get_records(field_name='files')
                product_init(data, self.schema)
                db.session.commit()
        except (InvalidRequestError, IntegrityError, UnmappedInstanceError, OperationalError) as e:
            flash(str(e), 'error')
            db.session.rollback()

        return redirect(self.url)

    # def is_accessible(self):
    #     return current_user.has_role('admin')


admin.add_view(MyModel(User, session=db.session, schema=UserSchema))
admin.add_view(MyModel(UserProfile, session=db.session, schema=UserProfileSchema))
admin.add_view(MyModel(Role, session=db.session))
admin.add_view(MyModel(UserRole, session=db.session, schema=UserRoleSchema))
admin.add_view(MyModel(PermissionSet, session=db.session))
