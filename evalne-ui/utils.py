import os
import shlex
import psutil
from subprocess import Popen


def start_process(cmd, verbose):
    """
    Runs the cmd command provided as input in a new process.

    Parameters
    ----------
    cmd : string
        A string indicating the command to run on the command line.
    verbose : bool
        Boolean indicating if the execution output should be shown or not (pipes stdout and stderr to devnull).

    Examples
    --------
    Runs a command that prints Start, sleeps for 5 seconds and prints Done

    >>> util.run("python -c 'import time; print(\"Start\"); time.sleep(5); print(\"Done\")'", True)
    Start
    Done

    """
    if verbose:
        sto = None
        ste = None
    else:
        devnull = open(os.devnull, 'w')
        sto = devnull
        ste = devnull

    Popen(shlex.split(cmd), stdout=sto, stderr=ste)
    print('EvalNE process started!')


def stop_process(process_name):
    proc = search_process(process_name)
    if proc is not None:
        proc.kill()
        print('EvalNE process killed!')


def search_process(process_name):
    for proc in psutil.process_iter():
        if process_name in shlex.join(proc.cmdline()):
            return proc
    return None
