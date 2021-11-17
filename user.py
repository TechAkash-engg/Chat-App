from werkzeug.security import check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class User:

    def __init__(self, username, user_id, email, password):
        self.username = username
        self.user_id = user_id
        self.email = email
        self.password = password

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.email

    def email(self):
       return self.email


    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)






