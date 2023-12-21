from serializer import Serializer


class UserSerializer(Serializer):
    fields = [
        "id",
        "phone_number",
        "first_name",
        "last_name",
    ]
