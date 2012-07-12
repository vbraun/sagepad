"""
User data
"""

database = dict()



def lookup_user(openid):
    """
    Return the :class:`User` with the given ``openid``
    """
    try:
        return database[openid]
    except KeyError:
        return None


def anonymous_user():
    return ANONYMOUS


class User(object):

    def __init__(self, openid, fullname, nickname, email=None):
        self._fullname = fullname
        self._nickname = nickname
        self._openid = openid
        self._email = email
        self._is_suspended = False
        database[openid] = self

    def __repr__(self):
        s = ', '.join(map(str,[self._openid, self._fullname, self._nickname, self._email]))
        return 'User('+ s + ')'

    def fullname(self):
        return self._fullname
    
    def nickname(self):
        return self._nickname

    def email(self):
        return self._email

    def is_authenticated(self):
        """
        Returns True if the user is authenticated
        
        That is, they have provided valid credentials. (Only
        authenticated users will fulfill the criteria of
        login_required.)
        """
        return self._openid is not None

    def is_active(self):
        """
        Returns True if this is an active user.

        In addition to being authenticated, they also have activated
        their account, not been suspended, or any condition your
        application has for rejecting an account. Inactive accounts
        may not log in (without being forced of course). 
        """
        return self.is_authenticated()

    def is_anonymous(self):
        """
        Returns True if this is an anonymous user. 
        (Actual users should return False instead.)
        """
        return self._openid is None

    def get_id(self):
        """
        """
        return self._openid




ANONYMOUS = User(None, 'Anonymous', 'Anonymous', None)

