from app.utils.serializers.serializer import Serializer


class UserSerializer(Serializer):
    fields = [
        "id",
        "phone_number",
        "first_name",
        "last_name",
        "created_at",
        "updated_at",
    ]
