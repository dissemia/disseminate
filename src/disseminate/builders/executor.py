"""
The pool executor for running multiple functions at once.
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from collections import namedtuple
import subprocess

from .exceptions import BuildError

# Setup a global pool for processes
executor = ThreadPoolExecutor(max_workers=cpu_count() * 2)

PopenResult = namedtuple('PopenResult', 'returncode args stdout stderr')


def run(timeout, **kwargs):
    """Run the command with the given arguments."""
    popen = subprocess.Popen(**kwargs, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=4096,)
    popen.wait(timeout=timeout)
    stdout, stderr = popen.communicate()
    return PopenResult(returncode=popen.returncode,
                       args=popen.args,
                       stdout=stdout.decode('latin1'),
                       stderr=stderr.decode('latin1'))


@staticmethod
def runtime_success(future):
    """Test whether a future from a subprocess is successful."""
    return future.result().returncode == 0


@staticmethod
def runtime_error(future, error_msg=None, raise_error=True):
    """Raise an error from a future working with subprocess"""
    popen_result = future.result()
    returncode = popen_result.returncode
    args = popen_result.args
    out = popen_result.stdout
    err = popen_result.stderr

    if error_msg is None:
        error_msg = ("The conversion command '{}' was "
                     "unsuccessful. Exited with code "
                     "{}.".format(' '.join(args), returncode))
    if raise_error:
        e = BuildError(error_msg)
        e.cmd = " ".join(args)
        e.returncode = returncode
        e.shell_out = out
        e.shell_err = err
        raise e
    else:
        logging.warning(error_msg)
        logging.debug(err)
