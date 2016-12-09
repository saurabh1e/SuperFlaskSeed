from src.utils import BaseView, AssociationView
from .resources import UserResource, UserProfileResource, UserRoleResource, RoleResource
from src import api


@api.register()
class UserListView(BaseView):
    resource = UserResource


@api.register()
class UserProfileListView(BaseView):
    resource = UserProfileResource


@api.register()
class RoleListView(BaseView):
    resource = RoleResource


@api.register()
class UserRoleAssociationView(AssociationView):

    resource = UserRoleResource
