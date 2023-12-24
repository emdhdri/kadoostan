from app.utils.serializers.serializer import Serializer


class UserSerializer(Serializer):
    def __init__(self, object):
        self.fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "created_at",
            "updated_at",
        ]
        super().__init__(object, self.fields)
