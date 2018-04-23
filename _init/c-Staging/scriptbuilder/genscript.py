#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools as itl

from utils import cfg as _cfg


def build_script(config, stagedict):
    # Read template file
    try:
        with open(config['engine']['template']) as f:
            template = f.read()
    except Exception as e:
        raise e

    # Format protocol with metadata
    script = template.format(**stagedict)

    # Write script to config dict
    scriptname = f"MD.{config['engine']['host']}" \
                 f".{config['systemname']}" \
                 f".run{stagedict['repl_num']:02d}" \
                 f".{stagedict['stage']}{stagedict['segment_num']:03d}.sh"
    config['scripts'][scriptname] = script


def build_equilibration_scripts(config):
    for repl_num, segment_num in itl.product(range(1, 1+config['engine']['replicates']),
                                             (0,)):
        stagedict = {
            'systemname':  config['systemname'],
            'repl_num':    repl_num,
            'stage':       "EQ",
            'segment_num': segment_num,
            'user_email':  config['engine']['user_email'],
            'logfiles':    "",
            'md_commands': "",
            'next_script_file': f"MD.{config['engine']['host']}"
                                f".{config['systemname']}"
                                f".run{repl_num:02d}"
                                f".MD{segment_num+1:03d}.sh"
        }

        # Add segment logfiles
        stagedict['logfiles'] += f"touch {config['systemname']}" \
                                 f".run{repl_num:02d}" \
                                 f".{stagedict['stage']}{segment_num:03d}" \
                                 f".out\n"
        stagedict['logfiles'] += f"touch {config['systemname']}" \
                                 f".run{repl_num:02d}" \
                                 f".{stagedict['stage']}{segment_num:03d}" \
                                 f".err\n"

        # Add logfiles for MD runs
        for eq_prot in config['equilibration_protocols']:
            logline = f"touch {config['systemname']}" \
                      f".run{repl_num:02d}" \
                      f".{stagedict['stage']}{segment_num:03d}" \
                      f".{eq_prot['stagename']}" \
                      f".logout\n"
            stagedict['logfiles'] += logline

        # Add md_commands
        restart_file = f"{config['systemname']}.prmcrd"
        for eq_prot in config['equilibration_protocols']:
            commandline = f"echo 'Running {eq_prot['stagename']}...'\n" \
                          f"pmemd.cuda -O -i MD.Amber.{eq_prot['stagename']}.conf \\\n" \
                          f"              -o {config['systemname']}.run{repl_num:02d}.{stagedict['stage']}{segment_num}.{eq_prot['stagename']}.logout \\\n" \
                          f"              -p {config['systemname']}.prmtop \\\n" \
                          f"              -c {restart_file} \\\n" \
                          f"              -ref {restart_file} \\\n" \
                          f"              -r {config['systemname']}.run{repl_num:02d}.from{eq_prot['stagename']}.rst \\\n" \
                          f"              -x {config['systemname']}.run{repl_num:02d}.{stagedict['stage']}{segment_num}.{eq_prot['stagename']}.netcdf\n\n"
            restart_file = f"{config['systemname']}.run{repl_num:02d}.from{eq_prot['stagename']}.rst"
            stagedict['md_commands'] += commandline

        build_script(config, stagedict)


def build_production_scripts(config):
    sim_prot = config['simulation_protocol']

    for repl_num, segment_num in itl.product(range(1, 1+config['engine']['replicates']),
                                             range(1, 1+config['simulation_protocol']['n_segments'])):
        stagedict = {
            'systemname':  config['systemname'],
            'repl_num':    repl_num,
            'stage':       "MD",
            'segment_num': segment_num,
            'user_email':  config['engine']['user_email'],
            'logfiles':    "",
            'md_commands': "",
            'next_script_file': f"MD.{config['engine']['host']}"
                                f".{config['systemname']}"
                                f".run{repl_num:02d}"
                                f".MD{segment_num+1:03d}.sh"
        }

        # Add segment logfiles
        stagedict['logfiles'] += f"touch {config['systemname']}" \
                                 f".run{repl_num:02d}" \
                                 f".{stagedict['stage']}{segment_num:03d}" \
                                 f".out\n"
        stagedict['logfiles'] += f"touch {config['systemname']}" \
                                 f".run{repl_num:02d}" \
                                 f".{stagedict['stage']}{segment_num:03d}" \
                                 f".err\n"

        # Add logfiles for MD runs
        stagedict['logfiles'] += f"touch {config['systemname']}" \
                                 f".run{repl_num:02d}" \
                                 f".{stagedict['stage']}{segment_num:03d}" \
                                 f".{sim_prot['stagename']}" \
                                 f".logout\n"

        # Add md_commands
        if segment_num == 1:
            restart_file = f"{config['systemname']}.run{repl_num:02d}.from{config['equilibration_protocols'][-1]['stagename']}.rst"
        else:
            restart_file = f"{config['systemname']}.run{repl_num:02d}.{stagedict['stage']}{segment_num-1:03d}.rst"

        stagedict['md_commands'] += f"echo 'Running {sim_prot['stagename']}...'\n" \
                                    f"pmemd.cuda -O -i MD.Amber.{sim_prot['stagename']}.conf \\\n" \
                                    f"              -o {config['systemname']}.run{repl_num:02d}.{stagedict['stage']}{segment_num:03d}.{sim_prot['stagename']}.logout \\\n" \
                                    f"              -p {config['systemname']}.prmtop \\\n" \
                                    f"              -c {restart_file} \\\n" \
                                    f"              -r {config['systemname']}.run{repl_num:02d}.{stagedict['stage']}{segment_num:03d}.rst \\\n" \
                                    f"              -x {config['systemname']}.run{repl_num:02d}.{stagedict['stage']}{segment_num:03d}.netcdf\n\n"

        build_script(config, stagedict)
