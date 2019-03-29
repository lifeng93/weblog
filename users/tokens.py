from datetime import date
from django.utils.http import int_to_base36
from django.conf import settings
import hmac
from django.utils.encoding import force_bytes
import hashlib


def salted_hmac(key_salt, value, secret=None):

    if secret is None:
        secret = settings.SECRET_KEY

    key_salt = force_bytes(key_salt)
    secret = force_bytes(secret)

    # We need to generate a derived key from our base key.  We can do this by
    # passing the key_salt and our base key through a pseudo-random function and
    # SHA1 works nicely.
    key = hashlib.sha1(key_salt + secret).digest()

    # If len(key_salt + secret) > sha_constructor().block_size, the above
    # line is redundant and could be replaced by key = key_salt + secret, since
    # the hmac module does the same thing for keys longer than the block size.
    # However, we need to ensure that we *always* do this.
    return hmac.new(key, msg=force_bytes(value), digestmod=hashlib.sha1)

# 'token': token_generator.make_token(user),

class EmailSetTokenGenerator:

    key_salt = "django.contrib.auth.tokens.EmailSetTokenGenerator"

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        # Used for mocking in testsi
        return date.today()


    def make_token(self, user):
        return self._make_token_with_timestamp(user, self._num_days(self._today()))


    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)
        hash = salted_hmac(
            self.key_salt,
            str(user.pk) + user.email + str(timestamp),
            secret=settings.SECRET_KEY,
        ).hexdigest()[::2]  # Limit to 20 characters to shorten the URL.
        return "%s-%s" % (ts_b36, hash)

# , base36_to_int
    # def check_token(self, user, token):
    #     """
    #     Check that a password reset token is correct for a given user.
    #     """
    #     if not (user and token):
    #         return False
    #     # Parse the token
    #     try:
    #         ts_b36, hash = token.split("-")
    #     except ValueError:
    #         return False

    #     try:
    #         ts = base36_to_int(ts_b36)
    #     except ValueError:
    #         return False

    #     expect_token = self._make_token_with_timestamp(user, ts)
    #     # Check that the timestamp has not been tampered with
    #     if not hmac.compare_digest(force_bytes(expect_token), force_bytes(token)):
    #         return False

    #     # Check the timestamp is within limit. Timestamps are rounded to
    #     # midnight (server time) providing a resolution of only 1 day. If a
    #     # link is generated 5 minutes before midnight and used 6 minutes later,
    #     # that counts as 1 day. Therefore,  1 means "at least 1 day, could be up to 2."
    #     if (self._num_days(self._today()) - ts) > 1:
    #         return False

    #     return True