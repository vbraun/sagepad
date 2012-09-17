

def PadOutput(data=None):
    """
    Recreate the pad output from a dictionary
    """
    if isinstance(data, PadOutput_Base):
        data = data.to_dict()
    if data is None:
        return PadOutput_Base({})
    if isinstance(data, basestring):
        return PadOutput_Base({'input':'', 'stdout':data, 'stderr':''})
    assert isinstance(data, dict)
    try:
        if 'class' in data:
            global pad_output_classes
            return pad_output_classes[data['class']](data)
        elif 'error' in data:
            return PadOutput_Error(data)
        elif 'output' in data:
            return PadOutput_RichText(data)
        elif 'stdout' in data:
            return PadOutput_StdIO(data)
    except KeyError:
        pass
    return PadOutput_Base({})
    


class PadOutput_Base(object):

    def __init__(self, data):
        if data is not None and 'class' in data:
            assert data['class'] == self.__class__.__name__

    def to_dict(self):
        """
        Save ``self`` as dictionary
        """
        return { 'class': str(self.__class__.__name__) }
    
    def text(self):
        return 'No output'

    def html(self):
        return '<div class="pad_output">No output</div>'



class PadOutput_Error(PadOutput_Base):
    
    def __init__(self, data):
        super(PadOutput_Error, self).__init__(data)
        self._input = data['input'].strip()
        self._error = data['error'].strip()
        self._stdout = data['stdout'].strip()
        self._stderr = data['stderr'].strip()

    def to_dict(self):
        d = super(PadOutput_Error, self).to_dict()
        d['input'] = self._input
        d['error'] = self._error
        d['stdout'] = self._stdout
        d['stderr'] = self._stderr
        return d

    def text(self):
        s = 'Error: ' + self._error + '\n'
        if len(self._stdout) > 0:
            s += r'stdout: ' + self._stdout + '\n'
        if len(self._stderr) > 0:
            s += r'stderr: ' + self._stderr + '\n'
        return s.strip()

    def html(self):
        import cgi
        s = '<div class="pad_error">' + self._error + '</div>\n'
        if len(self._stdout) > 0:
            s += r'<div class="pad_stdout">' + cgi.escape(self._stdout) + '</div>\n'
        if len(self._stderr) > 0:
            s += r'<div class="pad_stderr">' + cgi.escape(self._stderr) + '</div>\n'
        return s


class PadOutput_StdIO(PadOutput_Base):
    
    def __init__(self, data):
        super(PadOutput_StdIO, self).__init__(data)
        self._input = data['input'].strip()
        self._stdout = data['stdout'].strip()
        self._stderr = data['stderr'].strip()

    def to_dict(self):
        d = super(PadOutput_Error, self).to_dict()
        d['input'] = self._input
        d['stdout'] = self._stdout
        d['stderr'] = self._stderr
        return d

    def text(self):
        s = ''
        if len(self._stdout) > 0:
            s += 'Output: '+ self._stdout + '\n'
        if len(self._stderr) > 0:
            s += 'Error: ' + self._stderr + '\n'
        return s.strip()

    def html(self):
        import cgi
        s = ''
        if len(self._stdout) > 0:
            s += r'<div class="pad_stdout">' + cgi.escape(self._stdout) + '</div>\n'
        if len(self._stderr) > 0:
            s += r'<div class="pad_stderr">' + cgi.escape(self._stderr) + '</div>\n'
        return s
        

class PadOutput_RichText(PadOutput_Base):
    
    def __init__(self, data):
        super(PadOutput_RichText, self).__init__(data)
        self._input = data['input'].strip()
        self._stdout = data['stdout'].strip()
        self._stderr = data['stderr'].strip()
        self._output = data['output']

    def to_dict(self):
        d = super(PadOutput_RichText, self).to_dict()
        d['input'] = self._input
        d['stdout'] = self._stdout
        d['stderr'] = self._stderr
        d['output'] = self._output
        return d

    def text(self):
        s = ''
        for i, entry in enumerate(self._output):
            s += str(i) + '  "' + entry['input'] + '": '
            if entry['has_output']:
                s += entry['text/plain'] + ' ' + entry['type']
            else:
                s += 'No output' 
            s += '\n'
        if len(self._stdout) > 0:
            s += 'stdout: ' + self._stdout + '\n'
        if len(self._stderr) > 0:
            s += 'stderr: ' + self._stderr + '\n'
        return s

    def image_size(self, base64png):
        from PIL import Image
        import base64
        from StringIO import StringIO
        f = StringIO(base64.decodestring(base64png))
        image = Image.open(f)
        image.verify()
        return image.size

    def html(self):
        import cgi
        s = ''
        for i, entry in enumerate(self._output):
            if i == 0 and entry['type'] == '<type \'str\'>':
                continue  # skip the docstring
            #s += '<div class="pad_IOtag">In['+str(i)+']:'+'</div>\n'
            s += '<div class="pad_input">'+cgi.escape(entry['input'])+'</div>\n'
            if entry['has_output']:
                s += '<div class="pad_IOtag">Out['+str(i)+']:'+'</div>\n'
                s += '<div class="pad_output">'
                if entry['mime'] == 'image/png':
                    img = entry['image/png']
                    try:
                        w,h = self.image_size(img)
                        s += '<img src="data:image/png;base64,'
                        s += entry['image/png']
                        s += '" width='+str(w)+' height='+str(h)+'/>\n'
                    except Exception as e:
                        s += '<div class="error">Corrupt image: '+str(e)+'</div>\n'
                elif entry['mime'] == 'application/latex':
                    s += '$'+entry['application/latex']+'$'
                else:
                    s +=     entry['text/plain']
                s += '</div>\n'
                s += '<div class="pad_type">'
                s +=     cgi.escape(entry['type'])
                s += '</div>\n'
            s += '</div>\n'
        if len(self._stdout) > 0:
            s += '<div class="pad_input"><hr/></div>\n'
            s += r'<div class="pad_stdout">' + cgi.escape(self._stdout) + '</div>\n'
        if len(self._stderr) > 0:
            s += '<hr/>\n'
            s += r'<div class="pad_stderr">' + cgi.escape(self._stderr) + '</div>\n'
        return s






pad_output_classes = {
    PadOutput_Base.__name__: PadOutput_Base,
    PadOutput_Error.__name__: PadOutput_Error,
    PadOutput_StdIO.__name__: PadOutput_StdIO,
    PadOutput_RichText.__name__: PadOutput_RichText
}
