"""
The input/output data in a pad
"""

from pymongo import Connection, DESCENDING
from pymongo.objectid import ObjectId, InvalidId
from datetime import datetime

# always use Pad.get_database() to access the db
DATABASE = None



default_input = """'''
Untitled pad

Add some description here.
'''

# press Ctrl-Enter to evaluate!
print 'Hello, world!'
"""



class PadException(Exception):
    pass

class PadInvalidId(PadException):
    """
    The given ``pad_id`` is invalid
    """
    pass

class PadReadException(PadException):
    """
    You have insufficient permissions to view pad
    """
    pass

class PadWriteException(PadException):
    """
    You have insufficient permissions to modify pad
    """
    pass



class Pad(object):
    
    def __init__(self, data):
        """
        The Python constructor. You should use :meth:`make` or
        :meth:`lookup` to construct instances.
        """
        try:
            self._id = data['_id']
        except KeyError:
            self._id = None
        self._openid = data['openid']
        self._input  = data['input']
        self._output = data['output']
        self._title  = data['title']
        self._mode   = data['mode']
        self._public = data['public']
        self._ctime  = data['ctime']
        try: 
            self._mtime  = data['mtime']
        except KeyError:
            pass
        self._readonly = True

    def save(self):
        if self._readonly:
            raise PadWriteException('Cannot save, Pad is read only.')
        self._mtime = datetime.utcnow()
        self._title = self._guess_title()
        pad = {'openid'   : self._openid, 
               'input'    : self._input, 
               'output'   : self._output, 
               'title'    : self._title,
               'mode'     : self._mode,
               'public'   : self._public,
               'ctime'    : self._ctime,
               'mtime'    : self._mtime }
        db = Pad.get_database()
        if self._id is None:
            self._id = db.insert(pad)
        else:
            criterion = {'_id' : self._id}
            db.update(criterion, pad)

    def erase(self):
        if self._readonly:
            raise PadWriteException('Cannot erase, Pad is read only.')
        if self._id is None:
            return
        db = Pad.get_database()
        db.remove({'_id' : self._id})

    @staticmethod
    def make(openid, pad_input=None, pad_output=None, 
             title='Untitled', mode='sage', public=True):
        """
        Construct a new pad
        """
        if not isinstance(openid, basestring):
            openid = openid.get_id()
        if pad_input is None:
            global default_input
            pad_input = default_input
        pad = Pad({'openid' : openid, 
                   'input'  : pad_input,
                   'output' : pad_output,
                   'title'  : title,
                   'mode'   : mode,
                   'public' : public,
                   'ctime'  : datetime.utcnow()})
        pad._readonly = False
        pad.save()
        return pad

    @staticmethod
    def make_id(pad_id):
        """
        Construct a the pad_id from a string
        """
        try:
            return ObjectId(pad_id)
        except InvalidId:
            raise PadInvalidId('The pad_id is not valid.')

    def is_default(self):
        global default_input
        return self._input == default_input

    @staticmethod
    def lookup(pad_id, user):
        """
        Find the pad with given id in the database
        """
        if not isinstance(pad_id, ObjectId):
            pad_id = Pad.make_id(pad_id)
        db = Pad.get_database()
        data = db.find_one({'_id' :  pad_id})
        if data is None:
            raise PadInvalidId('The pad ID does not exist.')
        pad = Pad(data)
        if not pad.viewable_by(user):
            raise PadReadException('No read permission for pad')
        pad._readonly = not pad.editable_by(user)
        return pad

    @staticmethod
    def iterate(user, limit=None):
        """
        Iterate over the pads with given id in the database
        """
        db = Pad.get_database()
        for data in db.find({'openid' :  user.get_id()}).sort('mtime', DESCENDING):
            yield Pad(data)
            if limit is not None:
                limit -= 1
                if limit == 0:
                    return

    @staticmethod
    def get_database():
        """
        Return the database connection
        """
        global DATABASE
        if DATABASE is None:
            connection = Connection('localhost', 27017)
            DATABASE = connection.sagepad['pads']
        return DATABASE

    @staticmethod
    def max_pad_id():
        """
        Return the maximum pad id

        TODO: cache & increment whenever we add another pad
        """
        from pymongo.code import Code
        get_pad_id = Code(
            "function () {"
            "  this.pad_id.forEach(function(z) {"
            "    emit(z, 1);"
            "  });"
            "}")
        find_max = Code(
            "function (key, values) {"
            "  var maximum = 0;"
            "  for (var i = 0; i < values.length; i++) {"
            "    maximum = Math.max(maximum, values[i]);"
            "  }"
            "  return maximum;"
            "}")
        return Pad.get_database().map_reduce(get_pad_id, find_max)

    def _guess_title(self):
        """
        Guess the title from the module docstring or comment
        """
        fluff = [ '#', '//', '/*', '"""', "'''" ]
        found_fluff = False
        for line in self.get_input().splitlines():
            line.strip()
            for s in fluff:
                if line.startswith(s):
                    line = line[len(s):]
                    found_fluff = True
                line.strip()
            if line == '' or not found_fluff:
                continue
            return line
        return 'Untitled pad'
        

    def viewable_by(self, user):
        """
        Whether the user may view the pad
        """
        return True

    def editable_by(self, user):
        """
        Whether the user may edit the pad
        """
        return self._openid == user.get_id()

    def get_id(self):
        """
        Returns the mongo object id
        """
        return self._id

    def get_id_str(self):
        """
        Returns the mongo object id as string
        """
        return str(self._id)

    def get_ctime(self):
        return self._ctime

    def get_mtime(self):
        return self._mtime

    def pretty_mtime(self):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        time = self._mtime
        now = datetime.utcnow()
        diff = now - time 
        second_diff = diff.seconds
        day_diff = diff.days
        if day_diff < 0:
            return 'from future?'

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return  "a minute ago"
            if second_diff < 3600:
                return str( second_diff / 60 ) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str( second_diff / 3600 ) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff/7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff/30) + " months ago"
        return str(day_diff/365) + " years ago"


    def get_eval_mode(self):
        return self._mode

    def set_eval_mode(self, eval_mode):
        self._mode = eval_mode
        self.save()

    def get_input(self):
        return self._input

    def set_input(self, input):
        self._input = input
        self._mtime = datetime.utcnow()
        self.save()

    def get_output(self):
        return self._output

    def set_output(self, output):
        self._output = output
        self._mtime = datetime.utcnow()
        self.save()

    def get_title(self):
        return self._title
    
    def set_title(self, title):
        self._title = title
        self.save()


    
    
        
