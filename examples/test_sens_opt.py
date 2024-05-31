#%%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyvista as pv
from pathlib import Path

from mooseherder import MooseHerd
from mooseherder import InputModifier
from mooseherder import MooseRunner
from mooseherder import GmshRunner
from mooseherder import MooseConfig
from mooseherder import DirectoryManager
from mooseherder import ExodusReader
from mooseherder import SweepReader


from pymoo.algorithms.soo.nonconvex.nelder import NelderMead
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.core.problem import Problem
from pymoo.problems.static import StaticProblem

from pyfemop.optimisationmanager.optimisationmanager import OptimisationInputs
from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun
from pyfemop.optimisationmanager.costfunctions import CostFunction
from pycoatl.spatialdata.importsimdata import simdata_to_spatialdata

#%% Setup Problem

config = {'main_path': Path.home()/ 'projects/moose',
        'app_path': Path.home() / 'projects/sloth',
        'app_name': 'sloth-opt'}

moose_config = MooseConfig(config)

save_path = Path.cwd() / 'moose-config.json'
moose_config.save_config(save_path)

#moose_input = Path('/home/rspencer/moose_work/Chaboche_Sensitivity/models/creep_circ_para.i')
moose_input = Path('/home/rspencer/moose_work/Chaboche_Sensitivity/models/creep_two_side_para.i')
#Moose file itself is not modified. 
moose_modifier = InputModifier(moose_input,'#','')

#Modify the material input file directly 
neml2_input = Path('/home/rspencer/moose_work/Chaboche_Sensitivity/models/neml2/viscoplasticity_chaboche_mod.i')
neml2_modifier = InputModifier(neml2_input,'#','')

#Geometry parameterisation
#gmsh_input = Path('/home/rspencer/moose_work/Chaboche_Sensitivity/models/geometry/gmsh_circle_3d.geo')
gmsh_input = Path('/home/rspencer/moose_work/Chaboche_Sensitivity/models/geometry/two_side_2d.geo')
gmsh_modifier = InputModifier(gmsh_input,'//',';')

config_path = Path.cwd() / 'moose-config.json'
moose_config = MooseConfig().read_config(config_path)

moose_runner = MooseRunner(moose_config)
moose_runner.set_run_opts(n_tasks = 1,
                        n_threads = 1,
                        redirect_out = True)

gmsh_path = Path('/home/rspencer/src/gmsh/bin/gmsh')
gmsh_runner = GmshRunner(gmsh_path)

dir_manager = DirectoryManager(n_dirs=8)


sim_runners = [gmsh_runner,moose_runner]
input_modifiers = [gmsh_modifier,moose_modifier,neml2_modifier]

dir_manager.set_base_dir(Path('/home/rspencer/moose_work/Chaboche_Sensitivity/Run'))
dir_manager.clear_dirs()
dir_manager.create_dirs()

# Start the herd and create working directories
herd = MooseHerd(sim_runners,input_modifiers,dir_manager)
herd.set_num_para_sims(n_para=8)
herd.set_input_copy_name(['gmsh','moose','neml2'])

algorithm = PSO(pop_size=3,save_history=True)
input_params = {
    'p0' : [-2.5,0],
    'p1' : [2.5,5]
}

base_params = {
    'iso_sat_hard': 56.57169984728215,
    'iso_sat_rate': 1.2736565629075598,
    'yield': 15.87820418266938,
    'perz_ref': 50.15875209530555,
    'perz_exp': 4.480898137220765,
    #'x1_C': 2777.3983129476073,
    #'x1_g': 60.64664636665857,
    #'x1_A': 3.435165754894179e-08,
    #'x1_a': 1.3611312021677133
                }
oi = OptimisationInputs(input_params,algorithm,None,'sensitivity',base_params)
def testfunc():
    return 1
cf = CostFunction(simdata_to_spatialdata,[testfunc],10)
test = MooseOptimisationRun('Test',oi,herd,cf,None)
# %%
test.run(1)
# %%
