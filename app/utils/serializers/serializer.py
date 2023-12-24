from typing import Dict, Any


class Serializer:
    def __init__(self, object, fields=None):
        self.object = object
        self.fields = fields

    @property
    def data(self) -> Dict[str, Any]:
        serialized_data = {}
        for field in self.fields:
            serialized_data[field] = getattr(self.object, field, None)
        return serialized_data
