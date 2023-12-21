import mongoengine as me
from datetime import datetime



class User(me.Document):
    id = me.StringField(primary_key=True)
    phone_number = me.StringField(required=True, unique=True)
    first_name = me.StringField()
    last_name = me.StringField()
    token = me.StringField(unique=True)
    token_exp = me.DateTimeField()
    login_code = me.StringField()
    login_code_exp = me.DateTimeField()
    created_at = me.DateTimeField(default=datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.utcnow)
    
    def from_dict(self, data):
        if("id" in data):
            self.id = data["id"]
        if("phone_number" in data):
            self.id = data["phone_number"]
        if("first_name" in data):
            self.id = data["first_name"]
        if("last_name" in data):
            self.id = data["last_name"]
        self.created_at = datetime.utcnow
        self.updated_at = datetime.utcnow

        
        