#
#
# Import all necessary packages

import numpy as np

from pyfemop.optimizationmanager.optimizationmanager import MooseOptimizationRun
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooseherd import MooseRunner
from mooseherder.gmshrunner import GmshRunner
import copy

from pyfemop.optimizationmanager.costfunctions import CostFunction

from pymoo.termination import get_termination
from pyfemop.mooseutils.outputreaders import OutputExodusReader

print('---------------------------------')
print('          Example-1              ')
print('   Elastic modulus optimisation  ')
print('---------------------------------')

# Setup MOOSE Parameters
moose_dir = '/home/rspencer/moose'
moose_app_dir = '/home/rspencer/proteus'
moose_app_name = 'proteus-opt'
moose_input = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa_hole_plate.i'

moose_modifier = InputModifier(moose_input,'#','')
moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
moose_vars = [moose_modifier.get_vars()]

# Start the herd and create working directories
herd = MooseHerd(moose_runner,moose_modifier)
# Don't have to clear directories on creation of the herd but we do so here
# so that directory creation doesn't raise errors

herd.set_base_dir('/home/rspencer/mtgo/examples/')
herd.para_opts(n_moose=8,tasks_per_moose=1,threads_per_moose=1,redirect_out=True)

herd.clear_dirs()
herd.create_dirs()

# Create algorithm. Don't need MOO for this problem, but will use anyway.
algorithm = NSGA2(
pop_size=4,
n_offsprings=4,
sampling=FloatRandomSampling(),
crossover=SBX(prob=0.9, eta=15),
mutation=PM(eta=20),
eliminate_duplicates=True,
save_history = True
)
# Set termination criteria for optimisation
termination = get_termination("n_gen", 40)

# Define an objective function
def displacement_match(data):
    # Want to get the displacement at final timestep to be close to 0.0446297
    return np.abs(np.max(data)-0.0446297)

# Instance cost function
c = CostFunction(None,[displacement_match],None)

# Assign bounds
bounds  = {'e_modulus' : [0.5E9,2E9]}

# Create run
mor = MooseOptimizationRun('Ex1_Linear_Elastic',algorithm,termination,herd,c,bounds)

# Do 1 run.
mor.run(1)

