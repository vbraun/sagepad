

def PadOutput(data=None):
    """
    Recreated the pad output from a dictionary
    """
    from mime_type import MimeTypes
    if data is None:
        data = {'data': None, 'mime': str(MimeTypes.APP_UNKNOWN)}
    elif not isinstance(data, dict):
        data = {'data': str(data), 'mime': str(MimeTypes.TEXT_PLAIN)}
    from mime_type import MimeType
    mime = MimeType(data['mime'])
    pad_output = mime.make_pad_output(data)
    assert pad_output._mime == mime
    return pad_output



class PadOutput_ABC(object):

    def __init__(self, data):
        if data is None:
            self._output = None
        else:
            self._output = data['data']
            
    def to_dict(self):
        """
        Save ``self`` as dictionary
        """
        return {'mime': str(self._mime), 'data': self._output }
    
    def html(self):
        return self._output

    def mime(self):
        return self._mime


class PadOutputNone_class(PadOutput_ABC):
    def __init__(self, data=None):
        from mime_type import MimeTypes
        self._mime = MimeTypes.APP_UNKNOWN
        PadOutput_ABC.__init__(self, None)

class PadOutputText_class(PadOutput_ABC):
    def __init__(self, data):
        from mime_type import MimeTypes
        self._mime = MimeTypes.TEXT_PLAIN
        PadOutput_ABC.__init__(self, data)
        
