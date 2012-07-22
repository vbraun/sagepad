"""
User data
"""

from pymongo import Connection
from pymongo.objectid import ObjectId
from pad import Pad


# always use User.get_database() to access the db
DATABASE = None



class User(object):

    def __init__(self, data):
        self._fullname = data['fullname']
        self._nickname = data['nickname']
        self._openid = data['openid']
        try:
            self._email = data['email']
        except KeyError:
            self._email = None
        try:
            self._current_pad_id = data['pad_id']
        except KeyError:
            self._current_pad_id = None
        self._current_pad = None
        self._is_suspended = False

    @staticmethod
    def get_database():
        """
        Return the database connection
        """
        global DATABASE
        if DATABASE is None:
            connection = Connection('localhost', 27017)
            DATABASE = connection.sagepad['users']
        return DATABASE

    @staticmethod
    def anonymous():
        """
        Return the anonymous user
        """
        global ANONYMOUS
        return ANONYMOUS

    @staticmethod
    def lookup(openid):
        """
        Find the user with given ``openid`` or return None
        """
        db = User.get_database()
        u = db.find_one({'openid':openid})
        if u is None:
            return None
        else:
            return User(u)

    @staticmethod
    def make(self, openid, fullname, nickname, email=None):
        data = { 'openid'   : openid,
                 'fullname' : fullname,
                 'nickname' : nickname,
                 'email'    : email }
        user = User(data)
        user.save()

    def save(self):
        """
        Save ``self`` to the database
        """
        criterion = {'openid' : self._openid}
        user = {'openid'   : self._openid, 
                'fullname' : self._fullname, 
                'nickname' : self._nickname,
                'email'    : self._email,
                'pad_id'   : self._current_pad_id }
        User.get_database().update(criterion, user, upsert=True)
             
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
        Return the openid
        """
        return self._openid

    def set_current_pad(self, pad):
        if isinstance(pad, basestring):
            pad = ObjectId(pad)
        if isinstance(pad, ObjectId):
            if pad == self._current_pad_id:
                return
            pad = Pad.lookup(pad)
        if pad.get_id() == self._current_pad_id:
            return
        self._current_pad = pad
        self._current_pad_id = pad.get_id()
        self.save()

    def get_current_pad(self):
        """
        The current pad always exists; A new one is created if necessary.
        """
        if self._current_pad_id is None:
            self._current_pad = Pad.make(self.get_id())
            self._current_pad_id = self._current_pad.get_id()
            self.save()
        if self._current_pad is None:
            pad = Pad.lookup(self._current_pad_id)
            if pad is None:
                pad = Pad.make(self.get_id())
            self._current_pad = pad
            self._current_pad_id = self._current_pad.get_id()
            self.save()
        return self._current_pad

    def get_pad(self, pad_id):
        if not isinstance(pad_id, ObjectId):
            pad_id = ObjectId(pad_id)
        if pad_id == self._current_pad_id:
            return self.get_current_pad()
        return Pad.lookup(pad_id)

    def get_all_pads(self, limit=25):
        return list(Pad.iterate(self, limit))
            
        

ANONYMOUS = User({'openid':None, 'fullname':'Anonymous', 'nickname':'Anonymous', 'email':None})

