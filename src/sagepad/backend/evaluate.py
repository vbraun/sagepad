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
    stdoutfile = os.path.join(tmpdir, 'pad_stdout'+suffix)
    stderrfile = os.path.join(tmpdir, 'pad_stderr'+suffix)
    error = None
    with open(inputfile, 'w') as f:
        f.write(pad_input)
    os.environ['DOT_SAGE'] = os.path.join(tmpdir, 'dot_sage')
    os.environ['CCACHE_DISABLE'] = 'true'
    os.umask(0o0077)
    try:
        stdout_fd = open(stdoutfile, 'w')
        stderr_fd = open(stderrfile, 'w')
        cmd = subprocess.Popen(command+[inputfile], close_fds=True,
                               cwd=tmpdir,
                               stdout=stdout_fd,
                               stderr=stderr_fd)
        
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

        stdout_fd.close()
        stderr_fd.close()
    except Exception, msg:
        error = 'Unknown error: '+str(msg)

    with open(stdoutfile, 'r') as f:
        stdout = f.read(sizelimit)
    with open(stderrfile, 'r') as f:
        stderr = f.read(sizelimit)

    shutil.rmtree(tmpdir)
    d = { 'input': pad_input,
          'stdout': stdout, 
          'stderr': stderr }
    if error is not None:
        d['error'] = error
    return d




def evaluate_command_pipe(command, suffix, pad_input, timeout=10, sizelimit=1*1024*1024):
    tmpdir = tempfile.mkdtemp(prefix='sagepad-', suffix='.temp')
    stdoutfile = os.path.join(tmpdir, 'pad_stdout'+suffix)
    stderrfile = os.path.join(tmpdir, 'pad_stderr'+suffix)
    error = None
    os.environ['DOT_SAGE'] = os.path.join(tmpdir, 'dot_sage')
    os.environ['CCACHE_DISABLE'] = 'true'
    os.umask(0o0077)
    try:
        stdout_fd = open(stdoutfile, 'w')
        stderr_fd = open(stderrfile, 'w')
        cmd = subprocess.Popen(command, close_fds=True,
                               cwd=tmpdir,
                               stdin=subprocess.PIPE,
                               stdout=stdout_fd,
                               stderr=stderr_fd)
        cmd.stdin.write(pad_input)
        cmd.stdin.close()

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

        stdout_fd.close()
        stderr_fd.close()
    except Exception, msg:
        error = 'Unknown error: '+str(msg)

    with open(stdoutfile, 'r') as f:
        stdout = f.read(sizelimit)
    with open(stderrfile, 'r') as f:
        stderr = f.read(sizelimit)

    shutil.rmtree(tmpdir)
    d = { 'input': pad_input,
          'stdout': stdout, 
          'stderr': stderr }
    if error is not None:
        d['error'] = error
    return d
