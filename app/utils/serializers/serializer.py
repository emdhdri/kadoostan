class Serializer:
    fields = []

    def __init__(self, object):
        self.data = {}
        for field in self.fields:
            self.data[field] = getattr(object, field, None)
