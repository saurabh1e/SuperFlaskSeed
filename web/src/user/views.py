from src.utils import BaseView, AssociationView
from .resources import UserResource, UserProfileResource, UserRoleResource, RoleResource
from src import api


@api.register()
class UserView(BaseView):

    @classmethod
    def get_resource(cls):
        return UserResource


@api.register()
class UserProfileView(BaseView):

    @classmethod
    def get_resource(cls):
        return UserProfileResource


@api.register()
class RoleView(BaseView):

    @classmethod
    def get_resource(cls):
        return RoleResource


@api.register()
class UserRoleAssociationView(AssociationView):

    @classmethod
    def get_resource(cls):
        return UserRoleResource

