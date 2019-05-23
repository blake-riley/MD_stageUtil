#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import argparse
import pytraj as pt

from utils import cfg as _cfg
from pdbcheck import pdbcheck
from tleap import tleap
from scriptbuilder import genconf, genscript, writefiles


def main(config_file):
    print("---- CONFIGURATION ----")
    print(f"file:        {config_file.name}")

    try:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
        config_file.close()
    except Exception as e:
        raise e

    print(f"system:      {config['systemname']}")

    # If we don't have a topology/coordinate file specified in the config:====
    if not (config['structure']['topology']
            and config['structure']['coordinates']
            and os.path.isfile(config['structure']['topology'])
            and os.path.isfile(config['structure']['coordinates'])):

        # load pdb:===========================================================
        try:
            pdbstruct = pt.load(config['structure']['initial_pdb'])
        except Exception as e:
            raise e

        print(f"initial_pdb: {config['systemname']}")

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
              "---- 2d. Confirming disulfides ...              ----",
              "----     (will suggest all SG pairs within {} Å) ----".format(_cfg.DISULFIDE_SUGGESTION_CUTOFF),
              sep='\n')

        disulf_idxpairs = pdbcheck.confirm_disulfides(pdbstruct)

        # run tleap:==========================================================
        print("",
              "---- 3. Running tleap to create AMBER files ... ----", sep='\n')

        tleap.build_system(pdbstruct, config, disulf_idxpairs)

    # If we do have a topology/coordinate file:===========================
    else:
        print(f"topology:    {config['structure']['topology']}")
        print(f"coordinates: {config['structure']['coordinates']}")

    # for everything:=====================================================
    # build batch scripts for cluster runs:===============================
    print("",
          "---- 4. Building batch script files, and configuration files ... ----", sep='\n')

    genconf.build_equilibration_confs(config)
    genconf.build_production_conf(config)
    config['scripts'] = {}
    genscript.build_equilibration_scripts(config)
    genscript.build_production_scripts(config)

    writefiles.write_all_files(config)

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
