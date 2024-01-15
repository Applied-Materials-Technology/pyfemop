#
# To test run the optimization manager.
#
#%% Imports
import numpy as np

from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder.exodusreader import ExodusReader
#from mooseherder.outputreader import output_csv_reader

from pyfemop.optimisationmanager.costfunctions import CostFunction
from pyfemop.optimisationmanager.costfunctions import min_plastic
from pyfemop.optimisationmanager.costfunctions import creep_range
from pyfemop.optimisationmanager.costfunctions import max_stress
from pyfemop.optimisationmanager.costfunctions import avg_creep
from pymoo.termination import get_termination
import pickle
from matplotlib import pyplot as plt
import os
import sys
#from materialmodeloptimizer.fullfield.fullfielddata import FullFieldData
#from materialmodeloptimizer.fullfielddata.fullfielddatagrid import FullFieldDataGrid

#from mtgo.exodus import exomerge3
# Don't like the below but it works for now
sys.path.append(os.path.join('/home/rspencer/src/seacas',"lib"))
import exodus as exo

#%% Baseline run

efile = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa_hole_plate_out.e'

#f = exomerge.import_model(efile)
f = exo.exodus(efile,array_type='numpy')

# %% get some values
x_coords, y_coords, z_coords = f.get_coords()
f.get_variable_values('EX_ELEM_BLOCK',1,'stress_yy',1)
# %%
# Will need to iterate over timesteps to extract what we want. 
# Displacements basically. 
n_steps = f.numTimes
#f.get_node_variable_names()
#f.get_node_variable_values('disp_y',71)

#Get nodes on Visible-Surface side set
side_nodes,side_node_list=f.get_side_set_node_list(5)
surface_nodes = np.unique(side_node_list)-1 # Node the -1 (changes from 1 to 0 based indexing)

surface_x = x_coords[surface_nodes]
surface_y = y_coords[surface_nodes]
surface_z = z_coords[surface_nodes]

stress_yy = f.get_variable_values('stress_yy',72)
creep_yy = f.get_variable_values('stress_yy',72)
plastic_yy = f.get_variable_values('stress_yy',72)

# seems that I can't specifically get the export from the surface nodes.


# %%
f.variables()
# %%
f = ExodusReader('/home/rspencer/pyfemop/examples/moose-workdir-1/moose-sim-1_out.e')
# %%
