from django.contrib.auth.tokens import PasswordResetTokenGenerator
# import six

class MyPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp)

password_reset_token = MyPasswordResetTokenGenerator()