#
#
# Import all necessary packages

import numpy as np

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination import get_termination
from pymoo.termination.default import DefaultMultiObjectiveTermination

from pathlib import Path
from mooseherder.mooseconfig import MooseConfig
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder import MooseRunner
from mooseherder import DirectoryManager

from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun
from pyfemop.optimisationmanager.optimisationmanager import OptimisationInputs
from pyfemop.optimisationmanager.costfunctions import CostFunction
#from pyfemop.mooseutils.outputreaders import OutputExodusReader

print('------------------------------------------------')
print('                  Example-1                     ')
print('          Elastic modulus optimisation          ')
print('------------------------------------------------')

# Setup MOOSE Config
config = {'main_path': Path.home()/ 'projects/moose',
        'app_path': Path.home() / 'projects/sloth',
        'app_name': 'sloth-opt'}

moose_config = MooseConfig(config)

save_path = Path.cwd() / 'moose-config.json'
moose_config.save_config(save_path)


moose_input = Path('/home/rspencer/pyfemop/examples/scripts/ex1_linear_elastic.i')
moose_modifier = InputModifier(moose_input,'#','')

config_path = Path.cwd() / 'moose-config.json'
moose_config = MooseConfig().read_config(config_path)

moose_runner = MooseRunner(moose_config)
moose_runner.set_run_opts(n_tasks = 1,
                        n_threads = 1,
                        redirect_out = True)

dir_manager = DirectoryManager(n_dirs=4)





# Send all the output to the examples directory and clear out old output
# Start the herd and create working directories
# Don't have to clear directories on creation of the herd but we do so here
# so that directory creation doesn't raise errors
dir_manager.set_base_dir(Path('examples/'))
dir_manager.clear_dirs()
dir_manager.create_dirs()
# Start the herd and create working directories
herd = MooseHerd([moose_runner],[moose_modifier],dir_manager)
#herd.set_keep_flag(False)
# Set the parallelisation options, we have 8 combinations of variables and
# 4 MOOSE intances running, so 2 runs will be saved in each working directory
herd.set_num_para_sims(n_para=8)

# Create algorithm. Use SOO GA as only one objective
algorithm = GA(
pop_size=12,
eliminate_duplicates=True,
save_history = True
)

# Set termination criteria for optimisation
#termination = get_termination("n_gen", 2)
termination = DefaultMultiObjectiveTermination(
    xtol = 1e-3,
    cvtol = 1e-3,
    ftol = 1e-3,
    period = 3,
    n_max_gen = 20
)

# Define an objective function
def displacement_match(data,endtime,external_data):
    # Want to get the displacement at final timestep to be close to 0.0446297
    # Using simdata for now.
    #disp_y = data.node_vars['disp_y']
    disp_y = data.data_fields['displacement'].data[:,1,-1]
    #print(np.abs(np.max(disp_y)-0.0446297))
    
    return np.abs(np.max(disp_y)-0.0446297)

# Instance cost function
c = CostFunction([displacement_match],None)

# Assign bounds
bounds  = {'e_modulus' : [0.5E9,1.5E9]}
opt_inputs = OptimisationInputs(bounds,algorithm,None)

# Create run
mor = MooseOptimisationRun('ex1_Linear_Elastic',opt_inputs,herd,c)

# Do 1 run.
mor.run(20)

S = mor._algorithm.result().F 
X = mor._algorithm.result().X
print('Target Elastic Modulus = 1E9')
print('Optimal Elastic Modulus = {}'.format(X[0]))
print('Absolute Difference = {}'.format(X[0]-1E9))
print('% Difference = {}'.format(100*(X[0]-1E9)/X[0]))
print('The optimisation run is backed up to:')
print('{}'.format(mor.get_backup_path()))
print('This can be restored using MooseOptimisationRun.restore_backup().')