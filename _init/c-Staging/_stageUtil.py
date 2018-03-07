#!/usr/bin/env python3

_VERSION = "0.0.1.20180307"

DISULFIDE_SUGGESTION_CUTOFF = 4  # Å

#import os, sys
#import glob
import yaml
import argparse
import itertools as itl
import numpy as np
import pytraj as pt
import pdb4amber

def main(config_file):
    print("---- CONFIGURATION ----", sep='\n')
    print(f"file:   {config_file.name}")

    try:
        config = yaml.load(config_file)
        config_file.close()
    except Exception as e:
        raise e

    print(f"system: {config['systemname']}")

    print("",
          "---- 1. Investigating structure ... ----", sep='\n')
    print(f"pdb:    {config['structure']['initial_pdb']}")

    try:
        pdbstruct = pt.load(config['structure']['initial_pdb'])
    except Exception as e:
        raise e

    for i, mol in enumerate(pdbstruct.topology.mols):
        print(f"  molecule {i}:")
        begin_atom = pdbstruct.topology.atom(mol.begin_atom)
        begin_res = pdbstruct.topology.residue(begin_atom.resid)
        end_atom = pdbstruct.topology.atom(mol.end_atom - 1)
        end_res = pdbstruct.topology.residue(end_atom.resid)
        print(f"    residues: ({begin_res.name}`{begin_res.original_resid} -- {end_res.name}`{end_res.original_resid})\n" \
              f"    n_resid:  {1 + end_res.index - begin_res.index}\n" \
              f"    n_atoms:  {mol.end_atom - mol.begin_atom}")

    print("  Suggested disulfides:")
    disulf_idxpairs = []


    print("",
      "---- 2a. Final cleaning of structure with 'pdb4amber'... ----", sep='\n')

    ## TODO: input pdb4amber to validate pdb file
    ## pdb4amber script is at ~/.pyenv/versions/3.6.3/envs/pytraj-3.6.3/lib/python3.6/site-packages/pdb4amber/pdb4amber.py


    print("",
      "---- 2b. Double checking disulfides ... ----", sep='\n')

    # Suggest disulfides:
    def possible_disulfides():
        # Make distance function

        # Get atom indices for CYX/SG atoms
        aicyxsg = [a.index for a in pdbstruct.topology.atoms
                           if (a.resname == 'CYX' and a.name == 'SG')]
        # Get coordinates of these atoms
        coords_cyxsg = pdbstruct.xyz[0, aicyxsg, :]
        # Create an iter of ((idx1, idx2), (coord1, coord2)) structures
        all_disulf = zip(itl.combinations(aicyxsg, 2), itl.combinations(coords_cyxsg, 2))
        # Turn this into an iter of ((idx1, idx2), dist) structures
        all_disulf = ((idxs, np.linalg.norm(coord0 - coord1)) for (idxs, (coord0, coord1)) in all_disulf)
        # Filter these if dist <= DISULFIDE_SUGGESTION_CUTOFF
        all_disulf = filter(lambda id: id[1] <= DISULFIDE_SUGGESTION_CUTOFF, all_disulf)

        yield from all_disulf

    for idxs, dist in possible_disulfides():
        atm0 = pdbstruct.topology.atom(idxs[0])
        res0 = pdbstruct.topology.residue(atm0.resid)
        atm1 = pdbstruct.topology.atom(idxs[1])
        res1 = pdbstruct.topology.residue(atm1.resid)

        while True:
            yn = input(f"    {res0.name}`{res0.original_resid} -- {res1.name}`{res1.original_resid} ({dist:>6.3f} Å): [Y/n] ? ")

            if (yn == '') or (yn in 'Yy'):
                # User has requested default answer, or yes. Append this, and break from the input while-loop.
                disulf_idxpairs.append(idxs)
                break
            elif yn in 'Nn':
                # User has responded no disulfide. Break from the input while-loop.
                break
            else:
                # User hit a wrong key. Print error, loop again.
                print("      Please answer Y or N to the prompt.")
                continue

    ## TODO: verify against CONECT residues in the PDB, rename residues (as appropriate) to CYX for overrides

    print("",
      "---- 3. Running pytleap to create AMBER files ... ----", sep='\n')

    print("",
      "---- 4. Building batch script files, and configuration files ... ----", sep='\n')

    print("",
      "---- 5. Creating auxiliary script files ... ----", sep='\n')

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
│                        Version: v{_VERSION:>14.14} │▒▒
└─────────────────────────────────────────────────┘▒▒
  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒\n""")
    parser = argparse.ArgumentParser(description='Create ready-to-run simulations from a config file.')
    parser.add_argument('config_file',
                        type=argparse.FileType('r'),
                        help='a .json -type config file')
    args = parser.parse_args()

    main(args.config_file)
