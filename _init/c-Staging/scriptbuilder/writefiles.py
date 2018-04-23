#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil

from utils import cfg as _cfg


def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.isdir(dir):
        os.makedirs(dir)


def write_file(path, contents):
    try:
        with open(path, 'w') as f:
            f.write(contents)
    except Exception as e:
        raise e


def write_all_files(config):
    # Make sure the directories for each run are present
    for repl_num in range(1, 1+config['engine']['replicates']):
        assure_path_exists(f"run{repl_num:02d}/")

    # First, write scripts
    for filepath, filecontents in config['scripts'].items():
        write_file(filepath, filecontents)

    # Next, write configs
    for repl_num in range(1, 1+config['engine']['replicates']):
        for eq_prot in config['equilibration_protocols']:
            filepath = f"run{repl_num:02d}/MD.Amber.{eq_prot['stagename']}.conf"
            filecontents = eq_prot['protocol']
            write_file(filepath, filecontents)
        for sim_prot in (config['simulation_protocol'],):
            filepath = f"run{repl_num:02d}/MD.Amber.{sim_prot['stagename']}.conf"
            filecontents = sim_prot['protocol']
            write_file(filepath, filecontents)

    # Finally, copy in initial coordinates and topologies
    topfile = config['structure']['topology']
    crdfile = config['structure']['coordinates']

    for repl_num in range(1, 1+config['engine']['replicates']):
        topdest = f"run{repl_num:02d}/{topfile}"
        crddest = f"run{repl_num:02d}/{crdfile}"
        try:
            shutil.copy2(topfile, topdest)
            shutil.copy2(crdfile, crddest)
        except Exception as e:
            raise e
