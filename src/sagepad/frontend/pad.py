"""
The input/output data in a pad
"""

from pymongo import Connection
from pymongo.objectid import ObjectId
from datetime import datetime

# always use Pad.get_database() to access the db
DATABASE = None



default_input = """'''
Untitled pad

Add some description here.
'''

print 'Hello, world!'
"""




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
        self.save()

    def save(self):
        self._mtime = datetime.utcnow()
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

    @staticmethod
    def make(openid, pad_input=None, pad_output=None, 
             title='Untitled', mode='sage', public=True):
        """
        Construct a new pad
        """
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
        pad.save()
        return pad

    @staticmethod
    def lookup(pad_id):
        """
        Find the pad with given id in the database
        """
        db = Pad.get_database()
        data = db.find_one({'_id' :  ObjectId(pad_id)})
        if data is None:
            return None
        else:
            return Pad(data)

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
        


    def may_view(self, user):
        """
        Whether the user may view the pad
        """
        return True

    def may_edit(self, user):
        """
        Whether the user may edit the pad
        """
        return self._openid == user.get_id()

    def get_id(self):
        return self._pad_id

    def get_eval_mode(self):
        return self._mode

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


    
    
        
