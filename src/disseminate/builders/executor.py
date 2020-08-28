"""
The pool executor for running multiple functions at once.
"""
import logging
from concurrent.futures import ThreadPoolExecutor
import subprocess

from .exceptions import BuildError

# Setup a global pool for processes
executor = ThreadPoolExecutor()


def run(**kwargs):
    """Run the command with the given arguments."""
    popen = subprocess.Popen(**kwargs)
    popen.wait()
    return popen


@staticmethod
def runtime_success(future):
    """Test whether a future from a subprocess is successful."""
    return future.result().poll() == 0


@staticmethod
def runtime_error(future, error_msg=None, raise_error=True):
    """Raise an error from a future working with subprocess"""
    popen = future.result().poll()
    args = popen.args
    returncode = popen.returncode
    out, err = popen.communicate()
    out = out.decode('latin1')
    err = err.decode('latin1')

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