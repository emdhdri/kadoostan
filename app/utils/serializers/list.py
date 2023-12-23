from app.utils.serializers.serializer import Serializer


class GiftListSerializer(Serializer):
    fields = [
        "id",
        "name",
        "created_at",
        "updated_at",
    ]

    def __init__(self, object, include_user=False):
        if include_user:
            self.fields.append("user")
        super().__init__(object)
