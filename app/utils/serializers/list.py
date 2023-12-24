from app.utils.serializers.serializer import Serializer


class GiftListSerializer(Serializer):
    def __init__(self, object, include_user=False):
        self.fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
        ]
        if include_user:
            self.fields.append("user")
        super().__init__(object, self.fields)
