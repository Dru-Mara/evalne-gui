import os
import shlex
import psutil
from subprocess import Popen
from threading import Timer


class TimeoutExpired(Exception):
    pass


def start_process(cmd, verbose):
    """
    Runs the cmd command provided as input in a new process. If execution time exceeds timeout, the process is killed
    and a TimeoutExpired exception is raised.

    Parameters
    ----------
    cmd : string
        A string indicating the command to run on the command line.
    timeout : int or float
        A value indicating the maximum number of second the process is allowed to run for.
    verbose : bool
        Boolean indicating if the execution output should be shown or not (pipes stdout and stderr to devnull).

    Raises
    ------
    TimeoutExpired
        If the execution time exceeds the number of second indicated by timeout.

    Notes
    -----
    The method additionally raises ImportError, IOError and AttributeError if these are encountered during execution
    of the cmd command.

    Examples
    --------
    Runs a command that prints Start, sleeps for 5 seconds and prints Done

    >>> util.run("python -c 'import time; print(\"Start\"); time.sleep(5); print(\"Done\")'", 7, True)
    Start
    Done

    Same as previous command but now it does not print Done because it times out after 2 seconds

    >>> util.run("python -c 'import time; print(\"Start\"); time.sleep(5); print(\"Done\")'", 2, True)
    Start
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "EvalNE/evalne/utils/util.py", line 84, in run
        A string indicating the command to run on the command line.
    TimeoutExpired: Command `python -c 'import time; print("Start"); time.sleep(5); print("Done")'` timed out

    """
    if verbose:
        sto = None
        ste = None
    else:
        devnull = open(os.devnull, 'w')
        sto = devnull
        ste = devnull

    Popen(shlex.split(cmd), stdout=sto, stderr=ste)


def stop_process(process_name):
    proc = search_process(process_name)
    if proc is not None:
        proc.kill()
        print('Process `{}` killed'.format(proc.name()))


def search_process(process_name):
    # TODO: fix this!
    for proc in psutil.process_iter():
        if process_name in proc.cmdline():
            print('Process found: `{}`'.format(proc.name()))
            return proc
        else:
            print('Process not found.')
            return None
