# Chemotaxis-induced phase separation

This repository contains the code for the project *Chemotaxis-induced phase separation* 
by Henrik Weyer, David Muramatsu, and Erwin Frey. 

For the coarsening simulations in Fig. 2, we provide the COMSOL (`.mph`) setup files.
The analysis of these simulations was performed using the iPython notebooks `chymograph_log_time_rho0.03.ipynb`, `chymograph_log_time_rho0.03.ipynb` (Fig.2 (c)),
and `coarsening_analysis.ipynb` (Fig. 2 (d)).

The Mathematica notebooks to Fig. 3 (c, d) are `MinimalKSModel-logGrowth-ICSplitting-pub.nb` and `continuation-setup.nb`. 
The setup notebook must be in the same folder as `MinimalKSModel-logGrowth-ICSplitting-pub.nb` and is executed automatically as the initialization cells of `MinimalKSModel-logGrowth-ICSplitting-pub.nb` are executed.

## COMSOL Simulations
Simulations of the minimal Keller-Segel model are performed using the finite-element software COMSOL Multiphysics 
and with the settings provided in the presented setup files. The simulations were performed using COMSOL 6.0.
The conversion from COMSOL's output (`txt`) format to HDF5 format is performed using `createh5FromComsolTxt.py`.
The obtained `.hdf5` files are then used for the analysis within the iPython notebooks.

## Mathematica Notebooks
The enclosed Mathematica notebooks are written for Mathematica version 13.1. 
