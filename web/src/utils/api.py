import re
from flask_restful import Api
from flask_restful import Resource
from flask import request, jsonify, make_response

from .models import db
from .blue_prints import bp
from .exceptions import ResourceNotFound, SQLIntegrityError, SQlOperationalError, CustomException


def to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class ApiFactory(Api):
    def init_app(self, app):
        super().init_app(app)

    def register(self, **kwargs):

        def decorator(klass):
            document_name = klass.resource.model.__name__.lower()
            name = kwargs.pop('name', document_name)
            url = kwargs.pop('url', '/%s/' % to_underscore(klass.resource.model.__name__))
            endpoint = to_underscore(klass.__name__)
            view_func = klass.as_view(name)

            if klass.__bases__[0] == BaseDetailView:
                self.app.add_url_rule(url + '<string:slug>/', endpoint=endpoint, view_func=view_func,
                                      methods=['GET', "PATCH", 'DELETE'], **kwargs)
            elif klass.__bases__[0] == AssociationView:
                self.app.add_url_rule(url, endpoint=endpoint, view_func=view_func,
                                      methods=['PATCH'], **kwargs)
            else:
                self.app.add_url_rule(url, endpoint=endpoint, view_func=view_func,
                                      methods=['GET', "POST", "PUT"], **kwargs)
            return klass

        return decorator


api = ApiFactory(bp)


class BaseListView(Resource):
    resource = None

    def get(self):
        objects = self.resource().apply_filters(queryset=self.resource.model.query, **request.args)
        objects = self.resource().has_read_permission(request, objects)

        if '__order_by' in request.args:
            objects = self.resource().apply_ordering(objects, request.args['__order_by'])

        page = int(request.args['page']) if 'page' in request.args and request.args['page'] else 1
        per_page = int(request.args['per_page']) if 'per_page' in request.args \
                                                    and int(request.args['per_page']) < self.resource.max_limit \
            else self.resource.default_limit
        resources = objects.paginate(page=page, per_page=per_page)
        if resources.items:
            return make_response(jsonify({'success': True, 'data': self.resource.schema()
                                         .dump(resources.items, many=True).data, 'total': resources.total}), 200)
        return make_response(jsonify({'error': True, 'Message': 'No Resource Found'}), 404)

    def post(self):
        try:
            data, status = self.resource().save_resource(request)
        except (SQLIntegrityError, SQlOperationalError) as e:
            db.session.rollback()
            e.message['error'] = True
            return make_response(jsonify(e.message), e.status)
        return make_response(jsonify(data), status)

    def put(self):

        try:
            data, status = self.resource().update_resource(request, obj)
        except (SQLIntegrityError, SQlOperationalError) as e:
            db.session.rollback()
            e.message['error'] = True
            return make_response(jsonify(e.message), e.status)
        return make_response(jsonify(data), status)


class BaseDetailView(Resource):
    resource = None

    def get(self, slug):

        obj = self.resource.model.query.get(slug)
        if obj:
            obj = self.resource().has_read_permission(request, obj)
            return make_response(jsonify({'success': True, 'data': self.resource.schema().dump(obj, many=False).data})
                                 , 200)

        return make_response(jsonify({'error': True, 'message': 'Resource not found'}), 404)

    def patch(self, slug):
        obj = self.resource.model.query.get(slug)
        if not obj:
            return make_response(jsonify({'error': True, 'message': 'Resource not found'}), 404)
        try:
            data, status = self.resource().update_resource(request, obj)
        except (SQLIntegrityError, SQlOperationalError) as e:
            db.session.rollback()
            e.message['error'] = True
            return make_response(jsonify(e.message), e.status)
        return make_response(jsonify(data), status)

    def delete(self, slug):

        obj = self.resource.model.query.get(slug)
        if obj:
            if self.resource().has_delete_permission(request, obj):
                db.session.delete(obj)
                db.session.commit()
                return make_response(jsonify({}), 204)
            else:
                return make_response(
                    jsonify({'error': True, 'Message': 'Forbidden Permission Denied To Delete Resource'}), 403)
        return make_response(jsonify({'error': True, 'message': 'Resource not found'}), 404)


class AssociationView(Resource):

    resource = None

    def patch(self):

        data = request.json if isinstance(request.json, list) else [request.json]
        for d in data:
            try:
                db.session.begin_nested()
                if d['__action'] == 'add':
                    self.resource().add_relation(request, d)
                if d['__action'] == 'update':
                    self.resource().update_relation(request, d)
                elif d['__action'] == 'remove':
                    self.resource().remove_relation(request, d)
            except (ResourceNotFound, SQLIntegrityError, SQlOperationalError, CustomException) as e:
                db.session.rollback()
                e.message['error'] = True
                return make_response(jsonify(e.message), e.status)
        db.session.commit()

        return make_response(jsonify({'success': True, 'message': 'Updated Successfully', 'data': data}), 200)
