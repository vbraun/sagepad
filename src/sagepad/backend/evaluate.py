"""
Evaluate a command
"""


import tempfile
import shutil
import subprocess
import os
import signal



class AlarmException(Exception): 
    pass

def my_sigalarm_handler(sig, stack):
    raise AlarmException("timeout expired")


def evaluate_command(command, suffix, pad_input, timeout=10, sizelimit=1*1024*1024):
    tmpdir = tempfile.mkdtemp(prefix='sagepad-', suffix='.temp')
    inputfile  = os.path.join(tmpdir, 'pad_input'+suffix)
    outputfile = os.path.join(tmpdir, 'pad_output'+suffix)
    with open(inputfile, 'w') as f:
        f.write(pad_input)
    os.environ['DOT_SAGE'] = os.path.join(tmpdir, 'dot_sage')
    os.environ['CCACHE_DISABLE'] = 'true'
    os.umask(0o0077)
    with open(outputfile, 'w') as f:
        cmd = subprocess.Popen(command+[inputfile], close_fds=True,
                               stdout=f,
                               stderr=subprocess.STDOUT)
    
        # wait for any child to quit
        oldhandler = signal.signal(signal.SIGALRM, my_sigalarm_handler)
        signal.alarm(timeout)
        try:
            cmd.wait()
        except AlarmException:
            cmd.kill()
        finally:
            signal.signal(signal.SIGALRM, oldhandler)
            signal.alarm(0)

    with open(outputfile, 'r') as f:
        pad_output = f.read(sizelimit)

    shutil.rmtree(tmpdir)
    return pad_output

