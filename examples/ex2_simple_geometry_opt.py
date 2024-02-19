#
#
# Import all necessary packages

import numpy as np

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination.default import DefaultMultiObjectiveTermination

from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder import MooseRunner
from mooseherder import GmshRunner
from mooseherder import DirectoryManager
from mooseherder import MooseConfig
from pathlib import Path

from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun
from pyfemop.optimisationmanager.costfunctions import CostFunction

print('------------------------------------------------')
print('                  Example-2                     ')
print('          Simple Geometry Optimisation          ')
print('------------------------------------------------')

config = {'main_path': Path.home()/ 'projects/moose',
        'app_path': Path.home() / 'projects/sloth',
        'app_name': 'sloth-opt'}

moose_config = MooseConfig(config)

save_path = Path.cwd() / 'moose-config.json'
moose_config.save_config(save_path)


moose_input = Path('/home/rspencer/pyfemop/examples/scripts/ex2_simple_geometry.i')
moose_modifier = InputModifier(moose_input,'#','')

config_path = Path.cwd() / 'moose-config.json'
moose_config = MooseConfig().read_config(config_path)

moose_runner = MooseRunner(moose_config)
moose_runner.set_run_opts(n_tasks = 1,
                        n_threads = 1,
                        redirect_out = True)

dir_manager = DirectoryManager(n_dirs=4)


# Setup Gmsh

# Setup Gmsh
gmsh_input = Path('/home/rspencer/pyfemop/examples/scripts/gmsh_2d_simple_geom.geo')
gmsh_modifier = InputModifier(gmsh_input,'//',';')

gmsh_path = Path.home() / 'src/gmsh/bin/gmsh'
gmsh_runner = GmshRunner(gmsh_path)
gmsh_runner.set_input_file(gmsh_input)

# Setup herd composition
sim_runners = [gmsh_runner,moose_runner]
input_modifiers = [gmsh_modifier,moose_modifier]

dir_manager.set_base_dir(Path('examples/'))
dir_manager.clear_dirs()
dir_manager.create_dirs()

# Start the herd and create working directories
herd = MooseHerd(sim_runners,input_modifiers,dir_manager)
herd.set_num_para_sims(n_para=8)
# Don't have to clear directories on creation of the herd but we do so here
# so that directory creation doesn't raise errors


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
def stress_match(data,endtime,external_data):
    # Want to get the displacement at final timestep to be close to 0.0446297
    
    cur_stress = data.elem_vars[('vonmises_stress',1)]
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