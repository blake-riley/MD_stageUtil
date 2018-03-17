#!/usr/bin/env python

import os
import pty
import shutil
import subprocess


class PtyReplWrapper(object):
    def __init__(self, command):
        self.command = command

    def __enter__(self):
        # Hidden variables to be used
        self._subproc = None
        self._ptymaster, self._ptyslave = None, None

        # Spawn a new pseudo-tty, and make master non-blocking (will return errors if nothing to read)
        self._ptymaster, self._ptyslave = pty.openpty()
        os.set_blocking(self._ptymaster, False)

        # Print slavename
        assert os.isatty(self._ptyslave)
        print(f"New slave tty at {os.ttyname(self._ptyslave)}.")

        # Spawn _subproc
        self._subproc = subprocess.Popen(self.command,
                                         preexec_fn=os.setsid,
                                         stdin=self._ptyslave,
                                         stdout=self._ptyslave,
                                         stderr=self._ptyslave,
                                         universal_newlines=True)

        return self

    def __exit__(self, exit_type, exit_val, exit_traceback):
        # subprocess.poll() returns ExitCode
        # If subprocess is still running, kill program.
        if self._subproc.poll() is None:
            self._subproc.kill()

        def closefd(fd):
            """Close a fd with error catching if fd already closed."""
            try:
                os.close(fd)
            except OSError as e:
                # If the fd is already closed, we should get a "Bad file descriptor" error.
                # We will only silence this type of error.
                # Otherwise, it should be re-raised.
                if e.errno == 9:
                    pass
                else:
                    raise e

        # Close those file-descriptors & delete them.
        if hasattr(self, '_ptymaster'):
            closefd(self._ptymaster)
            del self._ptymaster
        if hasattr(self, '_ptyslave'):
            closefd(self._ptyslave)
            del self._ptyslave

    def poll(self):
        return self._subproc.poll()

    def write(self, data):
        # Must pass os.write a bytes-type object.
        if isinstance(data, str):
            data = data.encode()

        if not self.poll():  # If the process isn't dead
            bytesin = os.write(self._ptymaster, data)

        return bytesin  # Pass back to called the number of bytes written to the pty

    def read(self):
        out = None

        while not self.poll():  # If the process isn't dead
            try:
                buf = os.read(self._ptymaster, 512).decode()  # Grab a bunch of data.
                if not out:  # If we haven't had output yet, initialise 'out'
                    out = ""
                buf = buf.replace("\r\n", "\n")  # Convert newlines
                buf = buf.replace("\n\r", "\n")
                buf = buf.replace("\r", "")
                out += buf  # Add 'buf' to 'out'
            except BlockingIOError as e:
                if e.errno == 35:  # Resource temporarily unavailable, i.e. nothing to read!
                    break

        return out
