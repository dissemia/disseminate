"""
Build exceptions and utilities for build exceptions
"""
import logging


class BuildError(Exception):
    """A error was encountered in conducting a build."""


def runtime_error(popen, error_msg=None, raise_error=True):
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
