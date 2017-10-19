#!/usr/bin/env python

###################################
# VARIABLES TO EDIT
###################################

models = 	[
			 'Diabody.5iwl',
			 'Diabody.5gs2',
			 'Diabody.5gs2-noligand',
			 'Diabody.5gry',
			 'Diabody.5grx',
			 'Diabody.5grw',
			]

directories = ['../d-ParamGen/',
			   '../e-ConfGen/',
			   '../../run1/']

files = 	[
				('../d-ParamGen/{sysname}/', '_createAmberFiles.{sysname}.tleap.in'),
				#('../d-ParamGen/{sysname}/', '_shuffleIons.{sysname}.ptraj.in'),
				# ('../e-ConfGen/{sysname}/', '_createExtraBonds.{sysname}.tcl'),
				('../e-ConfGen/{sysname}/', '_createIndex.{sysname}.tcl'),
				('../../run1/{sysname}/', '_unwrapCenter.{sysname}.run1.tcl'),
			]

# NAMD Engine
# files.extend([
# 				('../e-ConfGen/{sysname}/', '_createBoxsize.{sysname}.tcl'),
# 				('../e-ConfGen/{sysname}/', '_createPR.{sysname}.tcl'),
# 				('../../run1/{sysname}/', '_MD.NAMD.{sysname}.EM.conf'),
# 				('../../run1/{sysname}/', '_MD.NAMD.{sysname}.EQheat.conf'),
# 				('../../run1/{sysname}/', '_MD.NAMD.{sysname}.EQdensity.conf'),
# 				('../../run1/{sysname}/', '_MD.NAMD.{sysname}.MD.conf'),
# 			])

# AMBER Engine
files.extend([
				('../../run1/{sysname}/', '_MD.Amber.EQ-a-min.conf'),
				('../../run1/{sysname}/', '_MD.Amber.EQ-b-heat.conf'),
				('../../run1/{sysname}/', '_MD.Amber.EQ-c-density.conf'),
				('../../run1/{sysname}/', '_MD.Amber.EQ-d-equil.conf'),
				('../../run1/{sysname}/', '_MD.Amber.MD.conf'),
			])

# Avoca (NAMD engine)
# files.extend([
# 				('../../run1/{sysname}/', '_MD.Avoca.{sysname}.run1.EQ000.sh'),
# 				('../../run1/{sysname}/', '_MD.Avoca.{sysname}.run1.MD001.sh'),
# 				('../../run1/{sysname}/', '_MD.Avoca.{sysname}.run1.MD002.sh'),
# 			])

# Orchard (NAMD engine)
# files.extend([
# 				('../../run1/{sysname}/', '_MD.Orchard.{sysname}.run1.EQ000.sh'),
# 				('../../run1/{sysname}/', '_MD.Orchard.{sysname}.run1.MD001.sh'),
# 				('../../run1/{sysname}/', '_MD.Orchard.{sysname}.run1.MD002.sh'),
# 			])

# MASSIVE (AMBER engine)
# files.extend([
# 				('../../run1/{sysname}/', '_MD.Massive.{sysname}.run1.EQ000.sh'),
# 				('../../run1/{sysname}/', '_MD.Massive.{sysname}.run1.MD001.sh'),
# 				('../../run1/{sysname}/', '_MD.Massive.{sysname}.run1.MD002.sh'),
# 			])

# MonARCH (AMBER engine)
files.extend([
				('../../run1/{sysname}/', '_MD.MonARCH.{sysname}.run1.EQ000.sh'),
				('../../run1/{sysname}/', '_MD.MonARCH.{sysname}.run1.MD001.sh'),
				('../../run1/{sysname}/', '_MD.MonARCH.{sysname}.run1.MD002.sh'),
			])

# Kronos (AMBER engine)
# files.extend([
# 				('../../run1/{sysname}/', '_MD.Kronos.{sysname}.run1.EQ000.sh'),
# 				('../../run1/{sysname}/', '_MD.Kronos.{sysname}.run1.MD001.sh'),
# 				('../../run1/{sysname}/', '_MD.Kronos.{sysname}.run1.MD002.sh'),
# 			])

# System information
system = 	{
				'sysname' : '',
				'lastletter' : 'd',
				'laststate' : 'cleaned',
				'finalletter' : 'e',
			}

###################################
# MAIN PROGRAM
###################################

import os
import errno

for directory in directories:
	for model in models:
		try:
			os.makedirs(directory + model)		#	Try to create every directory
		except OSError as e:					#	Catch all the errors (we're expecting cases where d already exists)
			if e.errno != errno.EEXIST:			#	If the error is something else, it's important.
				raise

for model in models:
	system['sysname'] = model
	for script in files:
		with open(script[1], 'r') as content_file:
   			content = content_file.read()
   		filename = script[0] + script[1][1:]
   		with open(filename.format(**system), 'w') as write_file:
			write_file.write(content.format(**system))
