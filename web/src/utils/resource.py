from sqlalchemy.exc import OperationalError, IntegrityError

from .models import db
from .exceptions import ResourceNotFound, SQLIntegrityError, SQlOperationalError, CustomException


class ModelResource(object):
    model = None
    schema = None

    filters = {}

    fields = ()

    max_limit = 100

    default_limit = 20

    related_resource = {}

    order_by = []

    only = ()

    exclude = ()

    def apply_filters(self, queryset, **kwargs):
        for k, v in kwargs.items():
            array_key = k.split('__')
            if array_key[0] == '' and array_key[1] in self.filters.keys():
                for operator in self.filters.get(array_key[1]):
                    if operator.op == array_key[2]:
                        queryset = operator().prepare_queryset(queryset, self.model, array_key[1], v)
        return queryset

    def apply_ordering(self, queryset, order_by):
        if order_by in self.order_by:
            queryset = queryset.order_by(getattr(self.model, order_by))
        return queryset

    def update_resource(self, request, obj):
        if self.has_change_permission(request, obj) and obj:
            obj, errors = self.schema(exclude=(self.related_resource.keys())).load(request.json, instance=obj, partial=True)
            if errors:
                db.session.rollback()
                return {'error': True, 'message': str(errors)}, 400

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                raise SQLIntegrityError(data=request.json, message='Integrity Error', operation='Adding Resource',
                                        status=400)
            except OperationalError:
                db.session.rollback()
                raise SQlOperationalError(data=request.json, message='Operational Error', operation='Adding Resource',
                                          status=400)
            return {'success': True, 'message': 'obj updated successfully',
                    'data': self.schema().dump(obj).data}, 200

        return {'error': True, 'Message': 'Forbidden Permission Denied To Change Resource'}, 403

    def save_resource(self, request):
        data = request.json if isinstance(request.json, list) else [request.json]
        objects, errors = self.schema().load(data, session=db.session, many=True)
        if errors:
            db.session.rollback()
            return {'error': True, 'message': str(errors)}, 400

        if self.has_add_permission(request, objects):
            db.session.add_all(objects)
        else:
            db.session.rollback()
            return {'error': True, 'Message': 'Forbidden Permission Denied To Add Resource'}, 403
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise SQLIntegrityError(data=data, message='Integrity Error', operation='Adding Resource', status=400)
        except OperationalError:
            db.session.rollback()
            raise SQlOperationalError(data=data, message='Operational Error', operation='Adding Resource', status=400)
        return {'success': True, 'message': 'Resource added successfully',
                'data': self.schema().dump(objects, many=True).data}, 201

    def has_read_permission(self, request, qs):
        return qs

    def has_change_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):
        return True


class AssociationModelResource(object):

    model = None

    schema = None

    associated_resources = {

    }

    def add_relation(self, request, data):
        obj, errors = self.schema().load(data, session=db.session)
        if errors:
            raise CustomException(data=data, message=str(errors), operation='adding relation')

        if self.has_add_permission(request, obj):
            db.session.add(obj)
            try:
                db.session.commit()
            except IntegrityError:
                raise SQLIntegrityError(data=data, message='Integrity Error', operation='adding relation', status=400)
            except OperationalError:
                raise SQLIntegrityError(data=data, message='Operational Error', operation='adding relation', status=400)
        else:
            raise ResourceNotFound(data=data, message='Permission Denied', operation='adding relation', status=404)

    def update_relation(self, request, data):
        obj = self.model.query.get(data['id'])
        if obj:
            obj, errors = self.schema().load(data, instance=obj)
            if errors:
                raise CustomException(data=data, message=str(errors), operation='updating relation')
            if self.has_change_permission(request, obj):
                raise CustomException(data=data, message='Permission Denied', operation='adding relation')
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                raise SQLIntegrityError(data=data, message='Integrity Error', operation='Adding Resource', status=400)
            except OperationalError:
                db.session.rollback()
                raise SQlOperationalError(data=data, message='Operational Error', operation='Adding Resource', status=400)
        else:
            raise ResourceNotFound(data=data, message='Object not Found', operation='Updating relation', status=404)

    def remove_relation(self, request, data):
        obj = self.model.query
        for k, v in data.items():
            if hasattr(self.model, k):
                obj = obj.filter(getattr(self.model, k) == v)
        obj = obj.first()
        if obj and self.has_delete_permission(request, obj):
            db.session.delete(obj)
            try:
                db.session.commit()
            except IntegrityError:
                raise SQLIntegrityError(data=data, message='Integrity Error', operation='deleting relation', status=400)
            except OperationalError:
                raise SQLIntegrityError(data=data, message='Operational Error', operation='deleting relation', status=400)
        else:
            raise ResourceNotFound(data=data, message='Object not Found', operation='deleting relation', status=404)

    def has_read_permission(self, request, qs):
        return qs

    def has_change_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):
        return True
