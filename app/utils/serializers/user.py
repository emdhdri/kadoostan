from app.utils.serializers import Serializer


class UserSerializer(Serializer):
    fields = [
        "id",
        "phone_number",
        "first_name",
        "last_name",
    ]
