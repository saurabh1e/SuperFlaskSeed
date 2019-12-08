from abc import ABC, abstractmethod
from typing import Type, List, Tuple

from flask import request
from sqlalchemy.exc import OperationalError, IntegrityError

from .exceptions import ResourceNotFound, SQLIntegrityError, SQlOperationalError, CustomException, RequestNotAllowed
from .models import db


class ModelResource(ABC):
    model = None
    schema = None

    filters = {}

    max_limit: int = 100

    default_limit: int = 50

    exclude_related_resource: Tuple[str] = ()

    order_by: List[str] = []

    only: Tuple[str] = ()

    exclude: Tuple[str] = ()

    include: Tuple[str] = ()

    optional: Tuple[str] = ()

    page: int = 1

    auth_required: bool = False

    export: bool = False

    max_export_limit: int = 5000

    roles_accepted: Tuple[str] = ()

    roles_required: Tuple[str] = ()

    def __init__(self):

        if request.args.getlist('__only'):
            if len(request.args.getlist('__only')) == 1:
                self.obj_only = tuple(request.args.getlist('__only')[0].split(','))
            else:
                self.obj_only = tuple(request.args.getlist('__only'))
        else:
            self.obj_only = self.only

        self.obj_exclude = []
        if request.args.getlist('__exclude'):
            if len(request.args.getlist('__exclude')) == 1:
                self.obj_exclude = request.args.getlist('__exclude')[0].split(',')
            else:
                self.obj_exclude = request.args.getlist('__exclude')

        self.obj_exclude.extend(list(self.exclude))
        self.obj_optional = list(self.optional)

        if request.args.getlist('__include'):
            if len(request.args.getlist('__include')) == 1:
                optionals = request.args.getlist('__include')[0].split(',')
            else:
                optionals = request.args.getlist('__include')

            for optional in optionals:
                try:
                    self.obj_optional.remove(optional)
                except ValueError:
                    pass

        self.obj_exclude.extend(self.obj_optional)

        self.page = int(request.args.get('__page')) if request.args.get('__page') else 1
        self.limit = int(request.args.get('__limit')) if request.args.get('__limit') \
                                                         and int(
            request.args.get('__limit')) <= self.max_limit else self.default_limit

    def apply_filters(self, queryset, **kwargs):
        for k, v in kwargs.items():
            array_key = k.split('__')
            if array_key[0] == '' and array_key[1] in self.filters.keys():
                for operator in self.filters.get(array_key[1]):
                    if operator.op == array_key[2]:
                        queryset = operator().prepare_queryset(queryset, self.model, array_key[1], v)

        if '__distinct_by' in request.args:
            queryset = queryset.distinct(getattr(self.model, request.args['__distinct_by']))
        return queryset

    def apply_ordering(self, queryset, order_by):
        desc = False
        if order_by.startswith('-'):
            desc = True
            order_by = order_by.replace('-', '')
        if order_by in self.order_by:
            if desc:
                queryset = queryset.order_by(getattr(self.model, order_by).desc())
            else:
                queryset = queryset.order_by(getattr(self.model, order_by))
        return queryset

    def patch_resource(self, obj):
        if self.has_change_permission(obj) and obj:
            obj, errors = self.schema().load(request.json, instance=obj, partial=True)
            if errors:
                db.session.rollback()
                return {'error': True, 'message': str(errors)}, 400

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                raise SQLIntegrityError(data={}, message='Integrity Error', operation='Adding Resource',
                                        status=400)
            except OperationalError:
                db.session.rollback()
                raise SQlOperationalError(data={}, message='Operational Error', operation='Adding Resource',
                                          status=400)
            return {'success': True, 'message': 'obj updated successfully',
                    'data': self.schema(exclude=tuple(self.obj_exclude), only=tuple(self.obj_only))
                            .dump(obj).data}, 200

        return {'error': True, 'message': 'Forbidden Permission Denied To Change Resource'}, 403

    def update_resource(self):
        data = request.json if isinstance(request.json, list) else [request.json]
        objects = []
        for d in data:
            obj = self.schema().get_instance(d)
            obj, errors = self.schema().load(d, instance=obj)
            if errors:
                db.session.rollback()
                return {'error': True, 'message': str(errors)}, 400

            if not self.has_change_permission(obj):
                db.session.rollback()
                return {'error': True, 'message': 'Forbidden Permission Denied To Add Resource'}, 403
            try:
                db.session.commit()
                objects.append(obj)
            except IntegrityError:
                db.session.rollback()
                raise SQLIntegrityError(data=d, message='Integrity Error', operation='Updating Resource', status=400)
            except OperationalError:
                db.session.rollback()
                raise SQlOperationalError(data=d, message='Operational Error', operation='Updating Resource',
                                          status=400)
        return {'success': True, 'message': 'Resource Updated successfully',
                'data': self.schema(exclude=tuple(self.obj_exclude), only=tuple(self.obj_only))
                    .dump(objects, many=True).data}, 201

    def save_resource(self):
        data = request.json if isinstance(request.json, list) else [request.json]
        objects, errors = self.schema().load(data, session=db.session, many=True)
        if errors:
            db.session.rollback()
            return {'error': True, 'message': str(errors)}, 400

        if self.has_add_permission(objects):
            db.session.add_all(objects)
        else:
            db.session.rollback()
            return {'error': True, 'message': 'Forbidden Permission Denied To Add Resource'}, 403
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print(e)
            raise SQLIntegrityError(data=data, message='Integrity Error', operation='Adding Resource', status=400)
        except OperationalError:
            db.session.rollback()
            raise SQlOperationalError(data=data, message='Operational Error', operation='Adding Resource', status=400)
        return {'success': True, 'message': 'Resource added successfully',
                'data': self.schema(exclude=tuple(self.obj_exclude), only=tuple(self.obj_only))
                    .dump(objects, many=True).data}, 201

    @abstractmethod
    def has_read_permission(self, qs) -> type(db.Model):
        return qs

    @abstractmethod
    def has_change_permission(self, obj) -> bool:
        return True

    @abstractmethod
    def has_delete_permission(self, obj) -> bool:
        return True

    @abstractmethod
    def has_add_permission(self, obj) -> bool:
        return True


class AssociationModelResource(ABC):
    model = None

    schema = None

    filters = {}

    max_limit: int = 100

    default_limit: int = 50

    exclude_related_resource: Tuple[str] = ()

    order_by: List[str] = []

    only: Tuple[str] = ()

    exclude: Tuple[str] = ()

    include: Tuple[str] = ()

    optional: Tuple[str] = ()

    page: int = 1

    auth_required = False

    roles_accepted: Tuple[str] = ()

    roles_required: Tuple[str] = ()

    def __init__(self):

        if request.args.getlist('__only'):
            if len(request.args.getlist('__only')) == 1:
                self.obj_only = tuple(request.args.getlist('__only')[0].split(','))
            else:
                self.obj_only = tuple(request.args.getlist('__only'))
        else:
            self.obj_only = self.only

        self.obj_exclude = []
        if request.args.getlist('__exclude'):
            if len(request.args.getlist('__exclude')) == 1:
                self.obj_exclude = request.args.getlist('__exclude')[0].split(',')
            else:
                self.obj_exclude = request.args.getlist('__exclude')

        self.obj_exclude.extend(list(self.exclude))
        self.obj_optional = list(self.optional)

        if request.args.getlist('__include'):
            if len(request.args.getlist('__include')) == 1:
                optionals = request.args.getlist('__include')[0].split(',')
            else:
                optionals = request.args.getlist('__include')

            for optional in optionals:
                try:
                    self.obj_optional.remove(optional)
                except ValueError:
                    pass

        self.obj_exclude.extend(self.obj_optional)

        self.page = int(request.args.get('__page')) if request.args.get('__page') else 1
        self.limit = int(request.args.get('__limit')) if request.args.get('__limit') \
                                                         and int(
            request.args.get('__limit')) <= self.max_limit else self.default_limit

    def apply_filters(self, queryset, **kwargs):
        for k, v in kwargs.items():
            array_key = k.split('__')
            if array_key[0] == '' and array_key[1] in self.filters.keys():
                for operator in self.filters.get(array_key[1]):
                    if operator.op == array_key[2]:
                        queryset = operator().prepare_queryset(queryset, self.model, array_key[1], v)

        return queryset

    def apply_ordering(self, queryset, order_by):
        desc = False
        if order_by.startswith('-'):
            desc = True
            order_by = order_by.replace('-', '')
        if order_by in self.order_by:
            if desc:
                queryset = queryset.order_by(getattr(self.model, order_by).desc())
            else:
                queryset = queryset.order_by(getattr(self.model, order_by))

        return queryset

    def add_relation(self, data):
        obj, errors = self.schema().load(data, session=db.session)
        if errors:
            raise CustomException(data=data, message=str(errors), operation='adding relation')

        if self.has_add_permission(obj, data):
            db.session.add(obj)
            try:
                db.session.commit()
            except IntegrityError as e:
                raise SQLIntegrityError(data=data, message=str(e), operation='adding relation', status=400)
            except OperationalError as e:
                raise SQLIntegrityError(data=data, message=str(e), operation='adding relation', status=400)
        else:
            raise RequestNotAllowed(data=data, message='Object not Found', operation='adding relation',
                                    status=401)

    def update_relation(self, data):
        obj = self.model.query.get(data['id'])
        if obj:
            obj, errors = self.schema().load(data, instance=obj)
            if errors:
                raise CustomException(data=data, message=str(errors), operation='updating relation')
            if self.has_change_permission(obj, data):
                raise CustomException(data=data, message='Permission Denied', operation='adding relation')
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                raise SQLIntegrityError(data=data, message='Integrity Error', operation='Adding Resource', status=400)
            except OperationalError:
                db.session.rollback()
                raise SQlOperationalError(data=data, message='Operational Error', operation='Adding Resource',
                                          status=400)
            else:
                raise RequestNotAllowed(data=data, message='Object not Found', operation='deleting relation',
                                        status=401)
        else:
            raise ResourceNotFound(data=data, message='Object not Found', operation='Updating relation', status=404)

    def remove_relation(self, data):
        obj = self.model.query
        for k, v in data.items():
            if hasattr(self.model, k):
                obj = obj.filter(getattr(self.model, k) == v)
        obj = obj.first()
        if obj:
            if self.has_delete_permission(obj, data):
                db.session.delete(obj)
                try:
                    db.session.commit()
                except IntegrityError:
                    raise SQLIntegrityError(data=data, message='Integrity Error', operation='deleting relation',
                                            status=400)
                except OperationalError:
                    raise SQLIntegrityError(data=data, message='Operational Error', operation='deleting relation',
                                            status=400)
            else:
                raise RequestNotAllowed(data=data, message='Object not Found', operation='deleting relation',
                                        status=401)
        else:
            raise ResourceNotFound(data=data, message='Object not Found', operation='deleting relation', status=404)

    @abstractmethod
    def has_read_permission(self, qs):
        return qs

    @abstractmethod
    def has_change_permission(self, obj, data) -> bool:
        return True

    @abstractmethod
    def has_delete_permission(self, obj, data) -> bool:
        return True

    @abstractmethod
    def has_add_permission(self, obj, data) -> bool:
        return True
