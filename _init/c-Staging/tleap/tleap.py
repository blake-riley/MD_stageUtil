#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.tleapwrapper import tleapInterface as TLI
from . import tleapcommands as tlcmds


def build_system(pdbstruct, config, disulf_idxpairs):
    # pytleap is installed as part of AMBERTools.
    # It's not doing anything special though---just writing things to a leap.cmd file, and then running the script file.
    # We can do better here, and run tleap line by line.

    # Unfortunately, it's not as simple as just wrapping tleap with subprocess, as tleap requires an interactive tty.
    # I've built a pseudo-tty (pty) repl wrapper to provide a nice "spoofed" interactive tty interface.
    #   # from utils.ptyreplwrapper import PtyReplWrapper
    # I then built a tleap wrapper so we can specifically wrap tleap (rather than just any tty-requiring program).
    #   # from utils.tleapwrapper import tleapInterface as TLI

    commands = []

    commands.append((tlcmds.tl_set_verbosity, ()))
    commands.append((tlcmds.tl_load_forcefields, (config,)))
    commands.append((tlcmds.tl_load_mol, (config,)))
    commands.append((tlcmds.tl_align_mol, ()))
    commands.append((tlcmds.tl_crosslink_disulfides, (pdbstruct, disulf_idxpairs)))
    commands.append((tlcmds.tl_explicit_solvate, (config,)))
    commands.append((tlcmds.tl_get_charge, ()))
    commands.append((tlcmds.tl_add_ions, (config,)))
    commands.append((tlcmds.tl_check_mol, ()))
    commands.append((tlcmds.tl_save_mol, (config,)))

    # Open a tleap
    with TLI() as proc:
        for (comm, args) in commands:
            try:
                comm(proc, *args)
            except Exception as e:
                raise e

        proc.runcommand('quit')  # Cleanly quit
