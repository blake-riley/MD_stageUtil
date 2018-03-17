#!/usr/bin/env python

import os
import time
import shutil
from .ptyreplwrapper import PtyReplWrapper


class tleapInterface(PtyReplWrapper):
    def __init__(self):
        # Try get a path for tleap
        self.path = shutil.which('tleap')  # Returns None if it doesn't exist
        # Assert tleap exists, and is an executable
        assert self.path, "tleap wasn't found in your PATH environment variable. Quitting."
        assert os.access(self.path, os.X_OK), f"The tleap I found in your PATH: {tleappath} isn't an executable!? Quitting."

        # The path to tleap is the executable we want to run. Pass this up!
        super().__init__(self.path)

    def __enter__(self):
        super().__enter__()
        time.sleep(0.25)  # It takes a while for stuff to get started

        _ = self.read()  # Read in the first lot of output from tleap, silencing it.

        return self

    def read(self):
        # tleap always spits out a "\n> " string when it's waiting for input.
        # We will use this as a marker that tleap has finished processing a command.
        # In this read() method, we continue reading until we're ready for input.
        out = None
        ready = False

        while not ready:
            buf = super().read()

            # If we get a None object back from super().read()
            # tleap hasn't gotten any input just yet (we beat the buffer!),
            # or has nothing to say. We should probably sleep a little.
            if not buf:
                time.sleep(0.1)
                continue

            if not out:  # If we haven't had output yet, initialise 'out'
                out = ""

            if buf[-3:] == "\n> ":  # If we have a prompt, we're ready.
                ready = True
                out += buf[:-3]  # Add everything _before_ the prompt to out.
            else:  # Otherwise, sleep and repeat
                time.sleep(0.1)
                out += buf

        return out

    def runcommand(self, command):
        """Send tleap a command, get the output, and return that output to the user."""
        if command[-1] != "\n":  # Make sure command finishes in a newline.
            command += "\n"
        bytesin = self.write(command)  # Send tleap a command
        return self.read()[bytesin:]  # Get output from tleap
