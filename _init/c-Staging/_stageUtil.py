#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import time
import subprocess
import yaml
import argparse
import itertools as itl
import numpy as np
import pytraj as pt
import pdb4amber

from utils import cfg as _cfg


def main(config_file):
    print("---- CONFIGURATION ----")
    print(f"file:   {config_file.name}")

    try:
        config = yaml.load(config_file)
        config_file.close()
    except Exception as e:
        raise e

    print(f"system: {config['systemname']}")

    # check input pdb:====================================================
    print("",
          "---- 1. Investigating structure ... ----", sep='\n')
    print(f"pdb:    {config['structure']['initial_pdb']}")

    try:
        pdbstruct = pt.load(config['structure']['initial_pdb'])
    except Exception as e:
        raise e

    solvent_mols = []

    for i, mol in enumerate(pdbstruct.topology.mols):
        begin_atom = pdbstruct.topology.atom(mol.begin_atom)
        begin_res = pdbstruct.topology.residue(begin_atom.resid)
        end_atom = pdbstruct.topology.atom(mol.end_atom - 1)
        end_res = pdbstruct.topology.residue(end_atom.resid)
        if not mol.is_solvent():
            print(f"  molecule {i}:")
            print(f"    residues: ({begin_res.name}`{begin_res.original_resid} -- {end_res.name}`{end_res.original_resid})\n"
                  f"    n_resid:  {1 + end_res.index - begin_res.index}\n"
                  f"    n_atoms:  {mol.end_atom - mol.begin_atom}")
        else:
            solvent_mols.append((begin_atom, begin_res))

    print(f"  {len(solvent_mols)} solvent molecules:")
    print(f"    ", end='')
    print(*(f"{begin_res.name}`{begin_res.original_resid}"
            for (begin_atom, begin_res) in solvent_mols),
          sep=', ')

    # find non-standard Amber residues:===================================
    print("",
          "---- 2a. Checking for unsupported AMBER residue names ... ----", sep='\n')

    ns_resids = set()
    for residue in pdbstruct.topology.residues:
        if residue.name not in pdb4amber.residue.AMBER_SUPPORTED_RESNAMES:
            ns_resids.add(residue)

    if ns_resids:
        print("############ NON-STANDARD RESIDUE NAMES FOUND ###########")
        print("### Amber will not understand the following residues: ###")
        for residue in ns_resids:
            idx0 = residue.first_atom_index
            atm0 = pdbstruct.topology.atom(idx0)
            chn0 = atm0.chain
            print(f"    ({chn0})//{residue.name}`{residue.original_resid}")
    else:
        print("  All residue names are standard AMBER resnames.")

    # count heavy atoms:==================================================
    print("",
          "---- 2b. Checking for missing heavy atoms ... ----", sep='\n')

    missing_atom_residues = []
    for residue in pdbstruct.topology.residues:
        if residue.name in pdb4amber.residue.HEAVY_ATOM_DICT:
            res_atoms = list(pdbstruct.topology.atom(i)
                             for i in range(residue.first_atom_index, residue.last_atom_index))
            heavy_atoms = set(atom.name
                              for atom in res_atoms
                              if atom.atomic_number != 1)
            n_heavy_atoms = len(heavy_atoms)
            n_missing = pdb4amber.residue.HEAVY_ATOM_DICT[residue.name] - n_heavy_atoms
            if n_missing > 0:
                residue_collection.append([residue, n_missing])

    if missing_atom_residues:
        print("  Missing heavy atom(s) in the following residues:")
        for residue, n_missing in missing_atom_residues:
            idx0 = residue.first_atom_index
            atm0 = pdbstruct.topology.atom(idx0)
            chn0 = atm0.chain

            print(f"    ({chn0})//{residue.name}`{residue.original_resid} is missing {n_missing} heavy atom(s)")
    else:
        print("  No missing heavy atoms.")

    # find possible gaps:==================================================
    print("",
          "---- 2c. Confirming chain breaks ... ----", sep='\n')

    CA_atoms = []
    C_atoms = []
    N_atoms = []
    gaplist = []

    #  N.B.: following only finds gaps in protein chains!
    for i, atom in enumerate(pdbstruct.topology.atoms):
        # TODO: if using 'CH3', this will be failed with ACE ALA ALA ALA NME system
        # if atom.name in ['CA', 'CH3'] and atom.residue.name in RESPROT:
        if atom.name in ['CA'] and atom.resname in pdb4amber.residue.RESPROT:
            CA_atoms.append(i)
        if atom.name == 'C' and atom.resname in pdb4amber.residue.RESPROT:
            C_atoms.append(i)
        if atom.name == 'N' and atom.resname in pdb4amber.residue.RESPROT:
            N_atoms.append(i)

    nca = len(CA_atoms)
    ngaps = 0

    for i in range(nca - 1):
        # Looking at the C-N peptide bond distance:
        C_atom = pdbstruct.topology.atom(C_atoms[i])
        N_atom = pdbstruct.topology.atom(N_atoms[i + 1])

        C_coord = pdbstruct.xyz[0, C_atoms[i]]
        N_coord = pdbstruct.xyz[0, N_atoms[i+1]]
        gap = np.linalg.norm(C_coord - N_coord)

        if gap > _cfg.CHAIN_BREAK_CUTOFF:
            gaprecord = (gap, C_atom, N_atom)
            gaplist.append(gaprecord)
            ngaps += 1

    if ngaps > 0:
        print("  Gaps found between the following residues:")
        for (dist, atm0, atm1) in gaplist:
            res0 = pdbstruct.topology.residue(atm0.resid)
            chn0 = atm0.chain
            res1 = pdbstruct.topology.residue(atm1.resid)
            chn1 = atm1.chain
            print(f"    ({chn0})//{res0.name}`{res0.original_resid}/{atm0.name} -- ({chn1})//{res1.name}`{res1.original_resid}/{atm1.name} ({dist:>6.3f} Å)")
    else:
        print("  No gaps between residues found.")

    while True:
        yn = input("  Are the identified gaps reasonable (if not, will abort): [Y/n] ? ")

        if (yn == '') or (yn in 'Yy'):
            # User has requested default answer, or yes. Break from the input while-loop.
            break
        elif yn in 'Nn':
            # User has responded unreasonable. Raise an exception to quit.
            raise AssertionError("User decided gaps were unreasonable. Aborting.")
            break
        else:
            # User hit a wrong key. Print error, loop again.
            print("    Please answer Y or N to the prompt.")
            continue

    # find possible S-S in the final protein:=============================
    print("",
          "---- 2d. Confirming disulfides ... ----", sep='\n')

    disulf_idxpairs = []

    # Suggest disulfides:
    def possible_disulfides():
        # Get atom indices for CYX/SG atoms
        aicyxsg = [a.index for a in pdbstruct.topology.atoms
                   if (a.resname == 'CYX' and a.name == 'SG')]
        # Get coordinates of these atoms
        coords_cyxsg = pdbstruct.xyz[0, aicyxsg, :]
        # Create an iter of ((idx1, idx2), (coord1, coord2)) structures
        all_disulf = zip(itl.combinations(aicyxsg, 2), itl.combinations(coords_cyxsg, 2))
        # Turn this into an iter of ((idx1, idx2), dist) structures
        all_disulf = ((idxs, np.linalg.norm(coord0 - coord1)) for (idxs, (coord0, coord1)) in all_disulf)
        # Filter these if dist <= _cfg.DISULFIDE_SUGGESTION_CUTOFF
        all_disulf = filter(lambda id: id[1] <= _cfg.DISULFIDE_SUGGESTION_CUTOFF, all_disulf)

        yield from all_disulf

    for (idx0, idx1), dist in possible_disulfides():
        atm0 = pdbstruct.topology.atom(idx0)
        res0 = pdbstruct.topology.residue(atm0.resid)
        chn0 = atm0.chain
        atm1 = pdbstruct.topology.atom(idx1)
        res1 = pdbstruct.topology.residue(atm1.resid)
        chn1 = atm1.chain

        while True:
            yn = input(f"    ({chn0})//{res0.name}`{res0.original_resid} -- ({chn1})//{res1.name}`{res1.original_resid} ({dist:>6.3f} Å): [Y/n] ? ")

            if (yn == '') or (yn in 'Yy'):
                # User has requested default answer, or yes. Append this, and break from the input while-loop.
                disulf_idxpairs.append((idx0, idx1))
                break
            elif yn in 'Nn':
                # User has responded no disulfide. Break from the input while-loop.
                break
            else:
                # User hit a wrong key. Print error, loop again.
                print("      Please answer Y or N to the prompt.")
                continue

    # TODO: verify against CONECT residues in the PDB, rename residues (as appropriate) to CYX for overrides

    print("",
          "---- 3. Running tleap to create AMBER files ... ----", sep='\n')

    # pytleap is installed as part of AMBERTools.
    # It's not doing anything special though---just writing things to a leap.cmd file, and then running the script file.
    # We can do better here, and run tleap line by line.

    # Unfortunately, it's not as simple as just wrapping tleap with subprocess, as tleap requires an interactive tty.
    # I've built a pseudo-tty (pty) repl wrapper to provide a nice "spoofed" interactive tty interface.
    #   # from utils.ptyreplwrapper import PtyReplWrapper
    # I then built a tleap wrapper so we can specifically wrap tleap (rather than just any tty-requiring program).
    from utils.tleapwrapper import tleapInterface as TLI

    # Open a tleap
    with TLI() as proc:
        pass

    proc = TLI().__enter__()
    proc.runcommand('hi')
    proc.__exit__(None, True, None)




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
