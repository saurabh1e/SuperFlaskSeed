from src.utils import BaseView, AssociationView
from .resources import OrderResource, InlineItemResource, TransferResource
from src import api


@api.register()
class OrderView(BaseView):

    @classmethod
    def get_resource(cls):
        return OrderResource


@api.register()
class InlineItemView(BaseView):

    @classmethod
    def get_resource(cls):
        return InlineItemResource


@api.register()
class TransferView(BaseView):

    @classmethod
    def get_resource(cls):
        return TransferResource

