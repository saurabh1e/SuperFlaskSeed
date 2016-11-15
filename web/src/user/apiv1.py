from src.utils import BaseDetailView, BaseListView, AssociationView
from .resources import UserResource, UserProfileResource, UserRoleResource, RoleResource
from src import api


@api.register()
class UserListView(BaseListView):
    resource = UserResource


@api.register()
class UserDetailView(BaseDetailView):
    resource = UserResource


@api.register()
class UserProfileListView(BaseListView):
    resource = UserProfileResource


@api.register()
class UserProfileDetailView(BaseDetailView):
    resource = UserProfileResource


@api.register()
class RoleListView(BaseListView):
    resource = RoleResource


@api.register()
class RoleDetailView(BaseDetailView):
    resource = RoleResource


@api.register()
class UserRoleAssociationView(AssociationView):

    resource = UserRoleResource
