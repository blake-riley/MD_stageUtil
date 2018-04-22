#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import argparse
import pytraj as pt

from utils import cfg as _cfg
from pdbcheck import pdbcheck
from tleap import tleap


def main(config_file):
    print("---- CONFIGURATION ----")
    print(f"file:   {config_file.name}")

    try:
        config = yaml.load(config_file)
        config_file.close()
    except Exception as e:
        raise e

    print(f"system: {config['systemname']}")

    # load pdb:===========================================================
    try:
        pdbstruct = pt.load(config['structure']['initial_pdb'])
    except Exception as e:
        raise e

    # check input pdb:====================================================
    print("",
          "---- 1. Investigating structure ... ----", sep='\n')
    print(f"pdb:    {config['structure']['initial_pdb']}")

    pdbcheck.describe_pdb(pdbstruct)

    # find non-standard Amber residues:===================================
    print("",
          "---- 2a. Checking for unsupported AMBER residue names ... ----", sep='\n')

    pdbcheck.check_unsupported_amber_residues(pdbstruct)

    # count heavy atoms:==================================================
    print("",
          "---- 2b. Checking for missing heavy atoms ... ----", sep='\n')

    pdbcheck.check_missing_heavy_atoms(pdbstruct)

    # find possible gaps:==================================================
    print("",
          "---- 2c. Confirming chain breaks ... ----", sep='\n')

    pdbcheck.confirm_chain_breaks(pdbstruct)

    # find possible S-S in the final protein:=============================
    print("",
          "---- 2d. Confirming disulfides ... ----", sep='\n')

    disulf_idxpairs = pdbcheck.confirm_disulfides(pdbstruct)

    # run tleap:==========================================================
    print("",
          "---- 3. Running tleap to create AMBER files ... ----", sep='\n')

    tleap.build_system(pdbstruct, config, disulf_idxpairs)

    # build batch scripts for cluster runs:===============================
    print("",
          "---- 4. Building batch script files, and configuration files ... ----", sep='\n')

    # add auxiliary scripts:==============================================
    print("",
          "---- 5. Creating auxiliary script files ... ----", sep='\n')

    # done:===============================================================
    print("",
          "---- Done! ----", sep='\n')


if __name__ == '__main__':
    print(f"""
┌─────────────────────────────────────────────────┐
│          _                   _   _ _   _ _      │
│      ___| |_ __ _  __ _  ___| | | | |_(_) |     │▒▒
│     / __| __/ _` |/ _` |/ _ \ | | | __| | |     │▒▒
│     \__ \ || (_| | (_| |  __/ |_| | |_| | |     │▒▒
│     |___/\__\__,_|\__, |\___|\___/ \__|_|_|     │▒▒
│                   |___/                         │▒▒
│                         Author:       Riley, BT │▒▒
│                        Version: v{_cfg._VERSION:>14.14} │▒▒
└─────────────────────────────────────────────────┘▒▒
  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒\n""")
    parser = argparse.ArgumentParser(description='Create ready-to-run simulations from a config file.')
    parser.add_argument('config_file',
                        type=argparse.FileType('r'),
                        help='a .json -type config file')
    args = parser.parse_args()

    main(args.config_file)
