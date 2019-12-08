from src.utils import ModelResource, operators as ops, AssociationModelResource
from .schemas import Order, OrderSchema, InlineItem, InlineItemSchema, Transfer, TransferSchema


class OrderResource(ModelResource):

    model = Order
    schema = OrderSchema

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class InlineItemResource(ModelResource):

    model = InlineItem
    schema = InlineItemSchema

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class TransferResource(ModelResource):

    model = Transfer
    schema = TransferSchema

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True
