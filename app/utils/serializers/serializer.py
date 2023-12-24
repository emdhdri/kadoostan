class Serializer:
    def __init__(self, object, fields=None):
        self.object = object
        self.fields = fields

    @property
    def data(self):
        serialized_data = {}
        for field in self.fields:
            serialized_data[field] = getattr(self.object, field, None)
        return serialized_data
