class Serializer:
    fields = []
    data = {}

    def __init__(self, object):
        for field in self.fields:
            self.data[field] = getattr(object, field, None)
