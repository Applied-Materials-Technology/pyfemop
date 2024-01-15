#
#
# Import all necessary packages

import numpy as np

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination.default import DefaultMultiObjectiveTermination

from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooseherd import MooseRunner
from mooseherder.mooseherd import GmshRunner

from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun
from pyfemop.optimisationmanager.costfunctions import CostFunction

print('------------------------------------------------')
print('                  Example-2                     ')
print('          Simple Geometry Optimisation          ')
print('------------------------------------------------')

# Setup MOOSE Parameters
moose_dir = '/home/rspencer/moose'
moose_app_dir = '/home/rspencer/proteus'
moose_app_name = 'proteus-opt'
moose_input = '/home/rspencer/pyfemop/examples/scripts/ex2_simple_geometry.i'

moose_modifier = InputModifier(moose_input,'#','')
moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
moose_vars = [moose_modifier.get_vars()]

# Setup Gmsh
gmsh_path = '/home/rspencer/src/gmsh/bin/gmsh'#os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
gmsh_input = '/home/rspencer/pyfemop/examples/scripts/gmsh_2d_simple_geom.geo'

gmsh_runner = GmshRunner(gmsh_path)
gmsh_runner.set_input_file(gmsh_input)
gmsh_modifier = InputModifier(gmsh_input,'//',';')

# Start the herd and create working directories
herd = MooseHerd(moose_runner,moose_modifier,gmsh_runner,gmsh_modifier)
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
#termination = get_termination("n_gen", 2)
termination = DefaultMultiObjectiveTermination(
    xtol = 1e-8,
    cvtol = 1e-6,
    ftol = 1e-6,
    period = 5,
    n_max_gen = 20
)

# Define an objective function
def stress_match(data,endtime):
    # Want to get the displacement at final timestep to be close to 0.0446297
    cur_stress = data['vonmises_stress']
    if cur_stress is not None:
        cost = np.abs(np.max(cur_stress)-6.0226E7)
    else:
        cost = 1E10                        
    return cost

# Instance cost function
c = CostFunction(None,[stress_match],None)

# Assign bounds
bounds  = {'neckWidth' : [0.5,1.]}

# Create run
mor = MooseOptimisationRun('ex2_simple_geometry',algorithm,termination,herd,c,bounds)

# Do run.
mor.run(20)

S = mor._algorithm.result().F 
X = mor._algorithm.result().X
print('Target Neck Width = 0.8')
print('Optimal Neck Width = {}'.format(X[0]))
print('Absolute Difference = {}'.format(X[0]-0.8))
print('% Difference = {}'.format(100*(X[0]-0.8)/X[0]))
print('The optimisation run is backed up to:')
print('{}'.format(mor.get_backup_path()))