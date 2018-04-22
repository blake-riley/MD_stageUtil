#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import cfg as _cfg


def tl_set_verbosity(proc):
    tlcomm = "verbosity 0"
    proc.runcommand(tlcomm)


def tl_load_forcefields(proc, config):
    cfg_forcefields = config['parameterisation']['forcefields']
    forcefields = [*cfg_forcefields['solute'],
                   *cfg_forcefields['solvent'],
                   *cfg_forcefields['other']]

    for ff in forcefields:
        print(f"  Loading forcefield: {ff}...")
        tlcomm = f"source {ff}"
        retval = proc.runcommand(tlcomm)
        retval = retval.splitlines()

        if _cfg.DEBUG_TLEAP:
            print("=========="*6)
            for line in retval:
                print(line)
            print("=========="*6)
        else:
            print(f"    {len(retval)} lines logged.")


def tl_load_mol(proc, config):
    pdbfile = config['structure']['initial_pdb']

    print(f"  Loading structure file: {pdbfile}...")
    tlcomm = f"mol = loadPdb {pdbfile}"
    retval = proc.runcommand(tlcomm)

    if _cfg.DEBUG_TLEAP:
        print("=========="*6)
        print(retval)
        print("=========="*6)


def tl_align_mol(proc):
    tlcomm = "alignAxes mol"
    proc.runcommand(tlcomm)


def tl_crosslink_disulfides(proc, pdbstruct, disulf_idxpairs):
    print("  Crosslinking disulfides...")
    for (idx0, idx1) in disulf_idxpairs:
        tlcommands = []

        atm0 = pdbstruct.topology.atom(idx0)
        res0 = pdbstruct.topology.residue(atm0.resid)
        chn0 = atm0.chain
        atm1 = pdbstruct.topology.atom(idx1)
        res1 = pdbstruct.topology.residue(atm1.resid)
        chn1 = atm1.chain

        print(f"    ({chn0})//{res0.name}`{res0.original_resid} -- ({chn1})//{res1.name}`{res1.original_resid}")
        tlcommands.append(f"desc \"({chn0})//{res0.name}`{res0.original_resid} -- ({chn1})//{res1.name}`{res1.original_resid}\"")
        tlcommands.append(f"crosslink mol.{res0.index+1} send mol.{res1.index+1} send")
        tlcommands.append(f"desc mol.{res0.index+1}.SG")
        tlcommands.append(f"desc mol.{res1.index+1}.SG")
        tlcommands.append("desc \"\"")

        retval = []
        for tlcomm in tlcommands:
            rv = proc.runcommand(tlcomm)
            retval.extend(rv.splitlines())

        if _cfg.DEBUG_TLEAP:
            print("=========="*6)
            for line in retval:
                print(line)
            print("=========="*6)
        else:
            print(f"      {len(retval)} lines logged.")


def tl_explicit_solvate(proc, config):
    print("  Solvating system with explicit water...")

    water_model = config['parameterisation']['water_model']
    pad = float(config['parameterisation']['water_padding'])
    print(f"    Using {water_model} to a minimum distance of {pad} Å")
    tlcomm = f"solvateBox mol {water_model} {pad}"

    proc.runcommand("desc \">>> Explicit solvation <<<\"")

    retval = proc.runcommand(tlcomm)
    retval = retval.splitlines()

    if _cfg.DEBUG_TLEAP:
        print("=========="*6)
        for line in retval:
            print(line)
        print("=========="*6)
    else:
        print(f"      {len(retval)} lines logged.")


def tl_get_charge(proc):
    print("  Getting charge of molecule...")

    tlcomm = "charge mol"
    retval = proc.runcommand(tlcomm)
    retval = retval.splitlines()

    if True:
        print("=========="*6)
        for line in retval:
            print(line)
        print("=========="*6)
    else:
        print(f"    {len(retval)} lines logged.")


def tl_add_ions(proc, config):
    print("  Adding ions...")

    ions = config['parameterisation']['ions']

    for ion, conc in ions.items():
        retval = []

        if conc == 0:
            print(f"    {ion} to neutralise")
        else:
            print(f"    {ion} to {conc} M")

        tlcomm = f"addIonsRand mol {ion} {conc}"
        rv = proc.runcommand(tlcomm)
        retval.extend(rv.splitlines())

        if _cfg.DEBUG_TLEAP:
            print("=========="*6)
            for line in retval:
                print(line)
            print("=========="*6)
        else:
            print(f"      {len(retval)} lines logged.")


def tl_check_mol(proc):
    print("  Checking system...")

    tlcomm = "check mol"
    retval = proc.runcommand(tlcomm)
    retval = retval.splitlines()

    if True:
        print("=========="*6)
        for line in retval:
            print(line)
        print("=========="*6)
    else:
        print(f"    {len(retval)} lines logged.")


def tl_save_mol(proc, config):
    print("  Saving parameterised system...")

    sysname = config['systemname']
    retval = []

    tlcomm = f"saveAmberParm mol {sysname}.prmtop {sysname}.prmcrd"
    rv = proc.runcommand(tlcomm)
    retval.extend(rv.splitlines())

    tlcomm = f"savePdb mol {sysname}.leap.pdb"
    rv = proc.runcommand(tlcomm)
    retval.extend(rv.splitlines())

    if True:
        print("=========="*6)
        for line in retval:
            print(line)
        print("=========="*6)
    else:
        print(f"      {len(retval)} lines logged.")
