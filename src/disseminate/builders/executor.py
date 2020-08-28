"""
The pool executor for running multiple functions at once.
"""
from concurrent.futures import ThreadPoolExecutor
import subprocess

# Setup a global pool for processes
executor = ThreadPoolExecutor()


def run(**kwargs):
    """Run the command with the given arguments."""
    popen = subprocess.Popen(**kwargs)
    popen.wait()
    return popen
