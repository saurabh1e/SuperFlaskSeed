from flask import request, make_response, redirect
from flask.json import jsonify
from flask_login import login_user
from flask_restful import Resource
from flask_security.utils import verify_and_update_password

from src.utils import BaseView, AssociationView
from .models import User
from .resources import UserResource, PartnerResource, PosOutletResource
from src import api


@api.register()
class UserView(BaseView):

    @classmethod
    def get_resource(cls):
        return UserResource


@api.register()
class PartnerView(BaseView):

    @classmethod
    def get_resource(cls):
        return PartnerResource


@api.register()
class PosOutletView(BaseView):

    @classmethod
    def get_resource(cls):
        return PosOutletResource


class UserLoginResource(Resource):
    model = User

    def post(self):
        if request.json:
            data = request.json

            user = self.model.query.filter(self.model.email == data['email']).first()
            if user and user.confirmed_at and verify_and_update_password(data['password'], user) and login_user(user):

                return make_response(jsonify({'id': user.id, 'authentication_token': user.get_auth_token()}), 200)
            else:
                return make_response(jsonify({'meta': {'code': 403}}), 403)

        else:
            data = request.form
            user = self.model.query.filter(self.model.email == data['email']).first()
            if user and verify_and_update_password(data['password'], user) and login_user(user):
                return make_response(redirect('/admin/', 302))
            else:
                return make_response(redirect('/api/v1/login', 403))

api.add_resource(UserLoginResource, '/login/', endpoint='login')

