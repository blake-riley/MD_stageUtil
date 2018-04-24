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

1. Clone this repo into a sensible directory name.
2. Create a copy of `templateconfig.yaml`, and call it something sensible: `SYSTEM.NAME.yaml`.
3. Edit the `SYSTEM.NAME.yaml` metadata file in your favourite text editor.
    - If you have built a topology and coordinate file already, you should specify these in this yaml file to skip straight to script-file generation.
4. Install the required packages for this project.
    - You should create a Python 3 virtualenvironment first.
    - In this virtualenvironment, run `pip install -r requirements.txt` to install the pre-requisite packages for this project.
5. From the root directory of this repo, run `python3 _init/c-Staging/stageUtil.py SYSTEM.NAME.yaml`, which will build scripts and a directory structure for simulation on a compute resource.
6. Push your cloned repo onto your favourite compute resource, and submit the `.sh` files to the queue as you normally would.


## Contributing

Contributing to this project is welcome, and you can do so in many ways!

If you have something that you think might require a lot of work, please create an issue on the issue tracker to start a discussion and get input from other contributors.

If you can fix the code yourself, please create a branch (or fork), edit the project, and then send a pull request.
