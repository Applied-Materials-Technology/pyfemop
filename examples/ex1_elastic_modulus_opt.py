#
#
# Import all necessary packages

import numpy as np

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination import get_termination

from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooseherd import MooseRunner

from pyfemop.optimizationmanager.optimizationmanager import MooseOptimizationRun
from pyfemop.optimizationmanager.costfunctions import CostFunction
from pyfemop.mooseutils.outputreaders import OutputExodusReader

print('---------------------------------')
print('          Example-1              ')
print('   Elastic modulus optimisation  ')
print('---------------------------------')

# Setup MOOSE Parameters
moose_dir = '/home/rspencer/moose'
moose_app_dir = '/home/rspencer/proteus'
moose_app_name = 'proteus-opt'
moose_input = '/home/rspencer/pyfemop/examples/scripts/ex1_linear_elastic.i'

moose_modifier = InputModifier(moose_input,'#','')
moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
moose_vars = [moose_modifier.get_vars()]

# Start the herd and create working directories
herd = MooseHerd(moose_runner,moose_modifier)
# Don't have to clear directories on creation of the herd but we do so here
# so that directory creation doesn't raise errors

herd.set_base_dir('/home/rspencer/pyfemop/examples/')
herd.para_opts(n_moose=4,tasks_per_moose=1,threads_per_moose=1,redirect_out=True)
herd.set_flags(one_dir = False, keep_all = True)

herd.clear_dirs()
herd.create_dirs()

# Create algorithm. Use SOO GA as only one objective
algorithm = GA(
pop_size=12,
eliminate_duplicates=True,
save_history = True
)
# Set termination criteria for optimisation
termination = get_termination("n_gen", 20)

# Define an objective function
def displacement_match(data,endtime):
    # Want to get the displacement at final timestep to be close to 0.0446297
    
    return np.abs(np.max(data['disp_y'])-0.0446297)

# Instance cost function
c = CostFunction(None,[displacement_match],None)

# Assign bounds
bounds  = {'e_modulus' : [0.5E9,1.5E9]}

# Create run
mor = MooseOptimizationRun('Ex1_Linear_Elastic',algorithm,termination,herd,c,bounds)

# Do 1 run.
mor.run(10)

S = mor._algorithm.result().F 
X = mor._algorithm.result().X
print('Target Elastic Modulus = 1E9')
print('Optimal Elastic Modulus = {}'.format(X[0]))
print('Absolute Difference = {}'.format(X[0]-1E9))
print('% Difference = {}'.format(100*(X[0]-1E9)/X[0]))