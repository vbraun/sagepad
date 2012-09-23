"""
Sage session with enhanced output

Example dictionary output in JSON format:

.. code-block:: json
    :linenos:

    {
      "input": "1+2+3;sin(x)/2; print \"printing\"; plot(sin); 1243"
      "preparsed": "Integer(1)+Integer(2)+ ...(preparsed input)... Integer(1243)", 
      "stdout": "printing\n", 
      "stderr": "", 
      "output_len": 5, 
      "output": [
        {
          "input": "Integer(1)+Integer(2)+Integer(3);", 
          "has_output": true, 
          "type": "<type 'sage.rings.integer.Integer'>", 
          "mime": "text/plain"
          "text/plain": "6", 
        }, 
        {
          "input": "sin(x)/Integer(2);", 
          "has_output": true, 
          "type": "<type 'sage.symbolic.expression.Expression'>", 
          "mime": "application/latex", 
          "application/latex": "\\frac{1}{2} \\, \\sin\\left(x\\right)", 
          "text/plain": "1/2*sin(x)"
        }, 
        {
          "input": "print \"printing\";", 
          "has_output": false
        }, 
        {
          "input": "plot(sin);", 
          "has_output": true, 
          "type": "<class 'sage.plot.graphics.Graphics'>", 
          "mime": "image/png", 
          "image/png": "iVBORw0KGgoAAAANSUhEUg ...(base64)... AAAASUVORK5C\nYII=\n", 
          "text/plain": "Graphics object consisting of 1 graphics primitive"
        }, 
        {
          "input": "Integer(1243)", 
          "has_output": true, 
          "type": "<type 'sage.rings.integer.Integer'>", 
          "mime": "text/plain"
          "text/plain": "1243", 
        }
      ], 
    }
"""

import tempfile
import shutil
import subprocess
import os
import signal
import sys

CODE_FILENAME = 'sage_session.py'
INPUT_FILENAME = 'pad_input.sage'
OUTPUT_FILENAME = 'pad_output.sage'


class AlarmException(Exception): 
    pass

def my_sigalarm_handler(sig, stack):
    raise AlarmException("timeout expired")

def my_sighup_handler(sig, stack):
    pass


    


class SageSession(object):
    """
    Control a :class:`SageRunner` instance running in another process
    """
    
    def _get_own_filename(self):
        fqn = os.path.join(os.getcwd(), __file__)
        # fqn points probably to sage_session.pyc
        dirname = os.path.dirname(fqn)
        global CODE_FILENAME
        return os.path.join(dirname, CODE_FILENAME)

    def __init__(self, timeout=10, sizelimit=1*1024*1024):
        self._timeout = timeout
        self._sizelimit = sizelimit
        global CODE_FILENAME, INPUT_FILENAME, OUTPUT_FILENAME
        self._tmpdir = tmpdir = tempfile.mkdtemp(prefix='sagepad-', suffix='.temp')
        shutil.copy(self._get_own_filename(), os.path.join(tmpdir, CODE_FILENAME))
        self._outputfile = os.path.join(tmpdir, OUTPUT_FILENAME)
        os.environ['DOT_SAGE'] = os.path.join(tmpdir, 'dot_sage')
        os.environ['CCACHE_DISABLE'] = 'true'
        os.umask(0o0077)
        self._log_stdout = os.path.join(tmpdir, 'stdout.log')
        self._log_stderr = os.path.join(tmpdir, 'stderr.log')
        self._log_stdout_fd = open(self._log_stdout, 'w')
        self._log_stderr_fd = open(self._log_stderr, 'w')
        self._cmd = subprocess.Popen(['sage', CODE_FILENAME], 
                                     cwd=tmpdir,
                                     close_fds=True,
                                     stdin=subprocess.PIPE,
                                     stdout=self._log_stdout_fd,
                                     stderr=self._log_stderr_fd)

    def wait_for_completion(self):
        oldhandler = signal.signal(signal.SIGALRM, my_sigalarm_handler)
        signal.alarm(self._timeout)
        try:
            self._cmd.wait()
        except AlarmException:
            self._cmd.kill()
        finally:
            signal.signal(signal.SIGALRM, oldhandler)
            signal.alarm(0)
        self._cmd.wait()
        self._log_stdout_fd.close()
        self._log_stderr_fd.close()

    def get_stdout(self):
        with open(self._log_stdout, 'r') as f:
            out = f.read(self._sizelimit)
        return out

    def get_stderr(self):
        with open(self._log_stderr, 'r') as f:
            err = f.read(self._sizelimit)
        return err
        
    def error_message(self, msg):
        d = { 'input': self._input, 'error': msg }
        return d

    def eval_dict(self, pad_input):
        self._input = pad_input
        self._cmd.stdin.write(pad_input)
        self._cmd.stdin.close()
        self.wait_for_completion()   # evaluating the inputfile
        import json
        from exceptions import EnvironmentError
        try:
            with open(self._outputfile, 'r') as f:
                pad_output = json.loads(f.read(self._sizelimit))
        except EnvironmentError:
            pad_output = self.error_message('No output received')
        except ValueError:
            pad_output = self.error_message('Evaluation unsuccessful')
        except Exception, msg:
            pad_output = self.error_message('Unknown error: '+str(msg))
        pad_output['stdout'] = self.get_stdout()
        pad_output['stderr'] = self.get_stderr()
        return pad_output

    def eval_json(self, pad_input):
        output = self.eval_dict(pad_input)
        import json
        return json.dumps(output, indent=2)

    def close(self):
        shutil.rmtree(self._tmpdir)
        



class CommandLogEntry(object):
    
    def __init__(self, command_log, lineno, col_offset):
        self._command_log = command_log
        self._lineno = lineno
        self._col_offset = col_offset
        self._has_output = False

    def index(self):
        return self._command_log._output.index(self)

    def is_first(self):
        out = self._command_log._output
        return self is out[0]

    def is_last(self):
        out = self._command_log._output
        return self is out[-1]

    def prev_entry(self):
        out = self._command_log._output
        i = out.index(self)
        return out[i-1]

    def next_entry(self):
        out = self._command_log._output
        i = out.index(self)
        return out[i+1]

    def set_output(self, value):
        self._has_output = True
        self._type = str(type(value))
        from sage.plot.graphics import is_Graphics
        from sage.symbolic.expression import is_Expression
        if is_Graphics(value):
            self._text = str(value)
            self._png = 'graphics_'+str(self.index())+'.png'
            self._mime = CommandLog.OUTPUT_PNG
            value.save(self._png, transparent=True)
        elif is_Expression(value):
            self._text = str(value)
            self._latex = str(value._latex_())
            self._mime = CommandLog.OUTPUT_LATEX
        else:
            self._text = value.__repr__()
            self._mime = CommandLog.OUTPUT_TEXT

    def __repr__(self):
        return self._text + ' ' + self._type

    def has_output(self):
        return self._has_output

    def get_text(self):
        return self._text
    
    def get_latex(self):
        return self._latex
    
    def get_type(self):
        return self._type

    def get_mime(self):
        return self._mime

    def get_input(self):
        txt = self._command_log.preparsed().splitlines()
        first_line = self._lineno-1
        first_col = self._col_offset
        if self.is_last():
            last_line = len(txt)-1
            last_col = len(txt[-1])
        else:
            last_line = self.next_entry()._lineno-1
            last_col = self.next_entry()._col_offset
        # return str(first_line) + '-'+str(last_line)+ ':' + str(first_col) + '-' +str(last_col)
        if first_line == last_line:
            cmd = txt[first_line][first_col:last_col]
        else:
            cmd = txt[first_line][first_col:]
            for line in range(first_line+1, last_line):
                cmd += txt[line]
            cmd += txt[last_line][:last_col]
        cmd = cmd.strip()
        return cmd

    def to_dict(self, base64=True):
        d = { 'input': self.get_input(),
              'has_output': self.has_output() }
        if self.has_output():
            d['type'] = self.get_type()
            d['mime'] = self.get_mime()
        if hasattr(self, '_text'): 
            d[CommandLog.OUTPUT_TEXT] = self.get_text()
        if hasattr(self, '_latex'): 
            d[CommandLog.OUTPUT_LATEX] = self.get_latex()
        if hasattr(self, '_png'):
            with open(self._png, 'r') as f:
                img = f.read()
            if base64:
                import base64
                img = base64.encodestring(img)
            d[CommandLog.OUTPUT_PNG] = img
        return d
                    

class CommandLog(object):

    OUTPUT_TEXT = 'text/plain'
    OUTPUT_LATEX = 'application/latex'
    OUTPUT_PNG = 'image/png'
    
    def __init__(self, cmd, tmpdir):
        self._input = cmd
        self._output = []
        self._tmpdir = tmpdir

    def preparsed(self):
        if '_preparsed' not in self.__dict__:
            from sage.misc.preparser import preparse
            self._preparsed = preparse(self._input, reset=True)
        return self._preparsed

    def new_entry(self, lineno, col_offset):
        entry = CommandLogEntry(self, lineno, col_offset) 
        self._output.append(entry)
        return entry
        
    def __len__(self):
        return len(self._output)

    def __repr__(self):
        s = ''
        for i, entry in enumerate(self._output):
            s += str(i) + '  "' + entry.get_input() + '": '
            if entry.has_output():
                s += entry.get_text() + ' ' + entry.get_type()
            else:
                s += 'No output' 
            s += '\n'
        return s

    def to_json(self):
        d = dict()
        d['input'] = self._input
        d['preparsed'] = self.preparsed()
        d['output_len'] = len(self)
        d['output'] = [ entry.to_dict() for entry in self._output ]
        import json
        return json.dumps(d)


class SageRunner(object):
    """
    The actual Sage session
    """

    def __init__(self):
        global INPUT_FILENAME, OUTPUT_FILENAME
        self._tmpdir = tmpdir = os.getcwd()
        self._outputfile = os.path.join(tmpdir, OUTPUT_FILENAME)
        self._outputfile_fd = open(self._outputfile, 'w')
        self._init_namespace()
        os.chdir(tmpdir)
        
    def _init_namespace(self):
        import sage.all_cmdline
        self._global_ns = dict(sage.all_cmdline.__dict__)
        self._local_ns = dict(sage.all_cmdline.__dict__)
        import __builtin__
        self._global_ns.setdefault('__builtin__', __builtin__)
        self._global_ns.setdefault('__builtins__', __builtin__)
        self._local_ns.setdefault('__builtin__', __builtin__)
        self._local_ns.setdefault('__builtins__', __builtin__)
        
    def save_output(self, msg):
        self._outputfile_fd.write(msg)

    def parse(self):
        import ast
        self._nodelist = ast.parse(self._log.preparsed())

    def node_iterator(self):
        return iter(self._nodelist.body)
        
    def _install_displayhook(self, log_entry):
        from sage.misc.html import html
        def my_displayhook(value):
            log_entry.set_output(value)
            global _
            _ = value
        self._old_displayhook = sys.displayhook
        sys.displayhook = my_displayhook

    def _uninstall_displayhook(self):
        sys.displayhook = self._old_displayhook
        
    def exec_node(self, node):
        import ast
        module = ast.Interactive([node])
        code = compile(module, '<input>', mode='single')
        entry = self._log.new_entry(node.lineno, node.col_offset)
        self._install_displayhook(entry)
        exec(code, self._global_ns, self._local_ns)
        self._uninstall_displayhook()
        self._global_ns.update(self._local_ns)

    def run(self):
        self._pad_input = sys.stdin.read()
        self._log = CommandLog(self._pad_input, self._tmpdir)
        self.parse()
        for node in self.node_iterator():
            self.exec_node(node)
        self.save_output(self._log.to_json())

    def close(self):
        self._outputfile_fd.close()
        

    


if __name__ == '__main__':
    cmd = sys.argv[-1]
    if cmd == CODE_FILENAME:
        app = SageRunner()
        app.run()
        app.close()
    else:
        app = SageSession()
        result = app.eval_dict(cmd)
        print '---' + ' output ' + '-' * 60
        print result.get('output', '')
        print '---' + ' error -' + '-' * 60
        print result.get('error', '')
        print '---' + ' stdout ' + '-' * 60
        print result['stdout']
        print '---' + ' stderr ' + '-' * 60
        print result['stderr']
        print '-' * 72
        app.close()
