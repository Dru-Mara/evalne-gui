#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 28/04/2022

import os
import shlex
import psutil
from subprocess import Popen


class EvalneProc(object):

    def __init__(self, proc=None):
        self._proc = proc

    def start(self, cmd, console_out, cwd=None, verbose=True):
        """ Starts a new process, if one is not already running, to execute the cmd command.

        Parameters
        ----------
        cmd : string
            A string indicating the command to run on the command line.
        console_out: string
            Path to a file where the stdout and stderr will writen.
        cwd : string
            The working directory for the new process spawned.
        verbose : bool
            Boolean indicating if the execution output should be shown or not (pipes stdout and stderr to devnull).

        Examples
        --------
        Runs a command that prints Start, sleeps for 5 seconds and prints Done

        >>> start_process("python -c 'import time; print(\"Start\"); time.sleep(5); print(\"Done\")'", True)
        Start
        Done

        """
        if self.running:
            if cwd is None:
                cwd = os.getcwd()
            if verbose:
                sto = open(console_out, 'w')
                ste = open(console_out, 'w')
            else:
                devnull = open(os.devnull, 'w')
                sto = devnull
                ste = devnull

            self._proc = Popen(shlex.split(cmd), stdout=sto, stderr=ste, cwd=cwd)

    def stop(self):
        """ Stops the process, if it is currently running. """
        if self.running:
            self._proc.kill()
            self._proc = None

    def info(self):
        """ Returns a summary of the main process stats as a dict. """
        pinfo = {
            'PID': self._proc.pid if self._proc else 'Unknown',
            'NAME': self._proc.name() if self._proc else 'Unknown',
            'CMD_LINE': ' '.join(self._proc.cmdline()) if self._proc else 'Unknown',
            'STATUS': self._proc.status() if self._proc else 'Unknown',
            'MEM%': '{:.2f} %'.format(self._proc.memory_percent()) if self._proc else 'Unknown',
            'CPU%': '{:.2f} %'.format(self._proc.cpu_percent(0)) if self._proc else 'Unknown',
            'CWD': self._proc.cwd() if self._proc else 'Unknown',
            'THREADS': self._proc.num_threads() if self._proc else 'Unknown',
        }
        return pinfo

    def running(self):
        return True if self._proc else False
