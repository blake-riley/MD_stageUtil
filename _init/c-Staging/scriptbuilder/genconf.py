#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import cfg as _cfg


def build_equilibration_confs(config):
    equilibration_protocols = config['equilibration_protocols']

    for eq_prot in equilibration_protocols:
        print("  Building protocol for {stagename}...".format(**eq_prot))

        # Read template file
        try:
            with open(eq_prot['template'], 'r') as f:
                protocol = f.read()
        except Exception as e:
            raise e

        # Format protocol with metadata
        protocol = protocol.format(**eq_prot)
        eq_prot['protocol'] = protocol

        # Print first line of protocol
        print("    " + protocol.splitlines()[0])


def build_production_conf(config):
    sim_prot = config['simulation_protocol']

    print("  Building protocol for {stagename}...".format(**sim_prot))

    # Read template file
    try:
        with open(sim_prot['template'], 'r') as f:
            protocol = f.read()
    except Exception as e:
        raise e

    # Calculate some protocol variables
    sim_prot['n_steps'] = int(1000 * sim_prot['segment_length'] / sim_prot['dt'])
    sim_prot['n_segments'] = int(sim_prot['total_length'] / sim_prot['segment_length'])

    # Format protocol with metadata
    protocol = protocol.format(**sim_prot)
    sim_prot['protocol'] = protocol

    # Print first line of protocol
    print("    " + protocol.splitlines()[0])
