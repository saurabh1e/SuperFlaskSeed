class Operators(object):
    op = 'exact'

    def prepare_queryset(self, query, model, key, value):
        return query.filter(getattr(model, key) == value)


class In(Operators):
    op = 'in'

    def prepare_queryset(self,query, model, key, values):
        return query.filter(getattr(model, key).in_(values))


class Equal(Operators):
    op = 'exact'

    def prepare_queryset(self, query, model, key, value):
        return query.filter(getattr(model, key) == value[0])


class Contains(Operators):
    op = 'contains'

    def prepare_queryset(self, query, model, key, value):
        return query.filter(getattr(model, key).contains(value[0]))


class Boolean(Operators):
    op = 'bool'

    def prepare_queryset(self, query, model, key, value):
        val = False if value[0] == 'false' else True
        return query.filter(getattr(model, key) == val)

