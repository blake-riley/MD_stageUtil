# MD_Project_Template

This project is a template directory structure (and collection of Python scripts!) for building Molecular Dynamics (MD) simulations. It contains templates for running MD simulations on a variety of Monash compute resources, using the [Amber Molecular Dynamics](http://ambermd.org) package.


## How is the template organised?

- `templateconfig.yaml` => The metadata file for your simulation. You can rename this to something more relevant to your project.
- `_init/` => The directory in which you'll be building .
  - `b-design/` => (Recommended) location for creating the initial pdb of your system.
  - `c-Staging/` => Contains most of the code in this project, as well as most of the template files.
    - `_templates/` => If you want to add a new computational resource for example, templates belong in the  subdirectory of here.
    - `stageUtil.py` => The master script of this project.
- `requirements.txt` => A list of python3 packages that are requirements of this project.
- `LICENSE` => terms of reuse (GNU GPL v3).


## How do I build a system?

There are multiple ways of doing things at each step. These different ways are listed "a.", "b.", etc. You only need to do one of these.

1. Get these files.  
    a. (With `git`): Clone this repo into a folder with a sensible name: `git clone https://gitlab.erc.monash.edu.au/BuckleLab/MD_Project_Template.git MD.20YYMMDD`  
    b. (Without `git`): Download the ['MD_Project_Template' archive](https://gitlab.erc.monash.edu.au/BuckleLab/MD_Project_Template/-/archive/master/MD_Project_Template-master.zip), and expand to a suitable location on your computer.
2. Copy the .pdb file of the system for which you wish to run MD into the 'MD_Project_Template' folder.
3. Create a copy of `templateconfig.yaml`, and call it something sensible: `SYSTEM.NAME.yaml`.
4. Edit the `SYSTEM.NAME.yaml` file in your favourite text editor to set the desired parameters for the MD you wish to perform. Most parameters can be left as their default values, but the following MUST be changed:
    - initial_pdb: set to the location of your initial input pdb file.
    - user_email: set to your Monash email address.
    - host: set to "Kronos", "Monarch", or whichever compute resource you want to run your MD.
    - topology/coordinates: replace with file names for manually generated tleap output.
5. Create a Python 3 virtualenvironment in which you can install the required packages for this project.  
    a. (With `pyenv`)  
        - Create a virtualenv: `pyenv virtualenv 3.6.6 mdprojecttemplate-3.6.6`  
        - Activate the virtualenv: `pyenv shell mdprojecttemplate-3.6.6`  
        - Install the prerequisites: `pip install -r requirements.txt`  
    b. (Without `pyenv`)  
        - Prevent version clashes between Python 2.7 and Python 3: `PYTHONPATH=''`  
        - If needed, install the virtualenvironment package: `pip3 install virtualenv`  
        - Create a Python 3 virtualenvironment in the current working directory: `virtualenv -p python3 .`  
        - Activate the virtualenvironment: `source ./bin/activate`  
        - In this virtualenvironment, install the pre-requisite packages for this project: `pip install -r requirements.txt`  
6. From the 'MD_Project_Template' folder (the root of this repo), run `python3 _init/c-Staging/stageUtil.py SYSTEM.NAME.yaml`, which will prepare scripts and a directory structure for your MD simulation on the nominated compute resource. These will be located in a series of folders denoted 'run01', 'run02', etc, according to how many runs you generated (three by default).
7. Copy these 'run' folders onto the computer resource specified in 'host' (Kronos, Monarch, etc.), and then submit the `.sh` files to the queue as you normally would.


## Contributing

Contributing to this project is welcome, and you can do so in many ways!

If you have something that you think might require a lot of work, please create an issue on the issue tracker to start a discussion and get input from other contributors.

If you can fix the code yourself, please create a branch (or fork), edit the project, and then send a pull request.
