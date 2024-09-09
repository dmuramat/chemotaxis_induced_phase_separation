# Chemotaxis-induced phase separation

In this repository, the code for the project *Chemotaxis-induced phase separation* 
by Henrik Weyer, David Muramatsu, and Erwin Frey is included. 

The code for the simulations and analysis for Fig. 2. is included in the COMSOL (`.mph`) setup files, 
and the iPython notebooks `chymograph_log_time_rho0.03.ipynb`, `chymograph_log_time_rho0.03.ipynb` (Fig.2 (c)),
and `coarsening_analysis.ipynb` (Fig. 2 (d)).

The Mathematica-notebooks to Fig. 3.(c, d) can be found in `MinimalKSModel-logGrowth-ICSplitting-pub.nb` and `continuation-setup.nb`. 
The setup-notebook must be executed before the other notebook in the same Kernel.

The nullclines in Fig. S1 (A-C) are taken from notebooks `minimalModelNullcline.nb` (A), `volumeExclusionNullcline.nb` (B), `receptorBindingNullcline.nb` (C).

## COMSOL Simulations
Simulations of the minimal Keller-Segel model are performed using the finite-element software COMSOL Multiphysics 
and with the settings provided in the present setup files. The simulations were performed using COMSOL 6.0.
The conversion from COMSOL's output (`txt`) format to HDF5 format is performed using `createh5FromComsolTxt.py`.
The obtained `.hdf5` files are then used for analysis.

## Mathematica Notebooks
The enclosed Mathematica notebooks are written for Mathematica version 13.1. 
