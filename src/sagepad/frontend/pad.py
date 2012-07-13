"""
The input/output data in a pad
"""


default_input = """'''
Untitled pad

Add some description here.
'''

print 'Hello, world!'
"""


database = dict()


def lookup_pad(pad_id):
    try:
        pad = database[pad_id]
    except KeyError:
        return None
    
    return Pad(pad_id)


class Pad(object):
    
    def __init__(self, user, pad_id):
        self._pad_id = pad_id
        self._openid = user.get_id()
        self._input = default_input
        self._output = ''
        self._title = 'Untitled'
        self._mode = 'sage'
        database[pad_id] = self

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

    def get_output(self):
        return self._output

    def set_output(self, output):
        self._output = output

    def get_title(self):
        return self._title
    
    def set_title(self, title):
        self._title = title


    
    
        
