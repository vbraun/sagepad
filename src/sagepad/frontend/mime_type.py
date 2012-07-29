
from pad_output import PadOutputNone_class, PadOutputText_class


def MimeType(mime):
    """
    Return the :class:`MimeType_class` defined by ``mime``
    """
    if isinstance(mime, MimeType_class):
        return mime
    mime = str(mime)
    for m in MimeTypes.list():
        if str(m) == mime:
            return m
    raise ValueError('the string '+str(mime)+' is not a known mime type.')


class MimeType_class(object):
    """
    A class encapsulating the mime type
    """

    def __init__(self, mime, pad_output_class):
        self._mime = mime
        self._pad_output_class = pad_output_class

    def __str__(self):
        return self._mime

    def make_pad_output(self, *args, **kwds):
        return self._pad_output_class(*args, **kwds)

        

class MimeTypes(object):
    """
    The known mime types
    """
    APP_UNKNOWN = MimeType_class('application/unknown', PadOutputNone_class)
    TEXT_PLAIN  = MimeType_class('text/plain', PadOutputText_class)

    @staticmethod 
    def list():
        return [ mime for mime in MimeTypes.__dict__.values() 
                 if isinstance(mime, MimeType_class) ]

