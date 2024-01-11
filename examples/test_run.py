#
# To test run the optimization manager.
#
#%% Imports
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
from mooseherder.exodusreader import ExodusReader
import copy

from pyfemop.optimizationmanager.costfunctions import CostFunction
from pyfemop.optimizationmanager.costfunctions import min_plastic
from pyfemop.optimizationmanager.costfunctions import creep_range
from pyfemop.optimizationmanager.costfunctions import maximise_strain
from pyfemop.optimizationmanager.costfunctions import maximise_strain_deviation
from pyfemop.optimizationmanager.costfunctions import avg_creep
from pymoo.termination import get_termination
import pickle
from matplotlib import pyplot as plt
from pyfemop.mooseutils.outputreaders import OutputExodusReader
from pycoatl.spatialdata.importmoose import moose_to_spatialdata
import pickle
#%% Baseline run
# Setup MOOSE
moose_dir = '/home/rspencer/moose'
moose_app_dir = '/home/rspencer/proteus'
moose_app_name = 'proteus-opt'
moose_input = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa_hole_plate.i'

moose_modifier = InputModifier(moose_input,'#','')
moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
moose_vars = [moose_modifier.get_vars()]

# Setup Gmsh
gmsh_path = '/home/rspencer/src/gmsh/bin/gmsh'#os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
#gmsh_input = '/home/rspencer/mtgo/data/gmsh_script_3d_gpa.geo'
gmsh_input = '/home/rspencer/mtgo/data/gmsh_hole_plate_creep_alt.geo'

gmsh_runner = GmshRunner(gmsh_path)
gmsh_runner.set_input_file(gmsh_input)
gmsh_modifier = InputModifier(gmsh_input,'//',';')

# Start the herd and create working directories
herd = MooseHerd(moose_runner,moose_modifier,gmsh_runner,gmsh_modifier)
# Don't have to clear directories on creation of the herd but we do so here
# so that directory creation doesn't raise errors
print(herd._base_dir)
herd.set_base_dir('/home/rspencer/mtgo/examples/')
herd.para_opts(n_moose=8,tasks_per_moose=1,threads_per_moose=1,redirect_out=True)
print(herd._base_dir)
herd.clear_dirs()
herd.create_dirs()

algorithm = NSGA2(
pop_size=8,
n_offsprings=8,
sampling=FloatRandomSampling(),
crossover=SBX(prob=0.9, eta=15),
mutation=PM(eta=20),
eliminate_duplicates=True,
save_history = True
)
termination = get_termination("n_gen", 40)
#c = CostFunction([min_plastic,max_stress],2.16E7)
reader = OutputExodusReader(True,0.2,data_range='last')
c = CostFunction(reader,[maximise_strain,maximise_strain_deviation],2.16E7)
#bounds  = {'p0' : [1.5,2.5],'p1' : [1.5,2.5],'p2' : [1.5,2.5]}
bounds  = {'h1x' : [-1.,1],'h1y' : [-0.5,0.5],'h1r' : [0.1,0.9],'h2x' : [-1.,1],'h2y' : [-0.5,0.5],'h2r' : [0.1,0.9]}
#bounds  =(np.array([1.,1.,1.]),np.array([2.5,2.5,2.5]))
#bounds  =(np.array([0.35,-0.5]),np.array([0.8,0.5]))
# Might need to fix the bounds issue, i.e. if model fails then penalise
#bounds  =(np.array([-1.,-0.5,0.1,-1.,-0.5,0.1]),np.array([1.,0.5,0.9,1.0,0.5,0.9]))
mor = MooseOptimizationRun('Run_SD_max_dev_circ_T',algorithm,termination,herd,c,bounds)

#%%
mor.run(1)



#%% Test pickling
pickle_path = '/home/rspencer/mtgo/examples/Run_SD_max_dev_circ.pickle'
with open(pickle_path,'rb') as f:
    morl = pickle.load(f,encoding='latin-1')

S = morl._algorithm.result().F 
X = morl._algorithm.result().X
print(X)
print(S)


# %%
S = mor._algorithm.result().F 
X = mor._algorithm.result().X
print(X)
print(S)
for i in range(X.shape[0]):
   plt.plot([X[i,0],X[i,1],X[i,2]],[5,0,-5])
#for i in range(X.shape[0]):
#    plt.plot([2.5,2.5*X[i,0],2.5],[-10,10*X[i,1],10])
#%%
for i in range(X.shape[0]):
    fig, ax = plt.subplots()
    rect = plt.Rectangle((-1,-1),2,2)

    #i=1
    circ1 = plt.Circle((X[i,0],X[i,1]),X[i,2],color='w')
    circ2 = plt.Circle((X[i,3],X[i,4]),X[i,5],color='w')
    ax.add_patch(rect)
    ax.add_patch(circ1)
    ax.add_patch(circ2)
    ax.set_xlim([-1,1])
    ax.set_ylim([-1,1])
    ax.set_title('{}'.format(i))
    

#%%
plt.scatter(S[:,0],S[:,1])
# %%
morl.run_optimal([0,1])
# %% 
#%% Test parallel reader
efile = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa_hole_plate_out.e'
reader = OutputExodusReader(False)
test = reader.read(efile)

#%%
dl = herd.read_results_para(reader)
c.evaluate_parallel(dl)

#%%
output_reader = OutputExodusReader(True,0.2E-3,data_range='last')
# %%
test= output_reader.read('/home/rspencer/mooseherder/examples/moose-workdir-1/moose-sim-1_out.e')
# %%
moose_dir = '/home/rspencer/moose'
moose_app_dir = '/home/rspencer/proteus'
moose_app_name = 'proteus-opt'
moose_input = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa.i'

moose_modifier = InputModifier(moose_input,'#','')
moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
moose_vars = [moose_modifier.get_vars()]

# Setup Gmsh
gmsh_path = '/home/rspencer/src/gmsh/bin/gmsh'#os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
gmsh_input = '/home/rspencer/mtgo/data/gmsh_script_3d_gpa.geo'

gmsh_runner = GmshRunner(gmsh_path)
gmsh_runner.set_input_file(gmsh_input)
gmsh_modifier = InputModifier(gmsh_input,'//',';')

# Start the herd and create working directories
herd = MooseHerd(moose_runner,moose_modifier,gmsh_runner,gmsh_modifier)
# Don't have to clear directories on creation of the herd but we do so here
# so that directory creation doesn't raise errors
herd.set_base_dir('/home/rspencer/mtgo/examples/')
herd.para_opts(n_moose=8,tasks_per_moose=1,threads_per_moose=1,redirect_out=True)

# %%
herd.read_all_output_keys()
files = herd.get_output_files()
# %%
reader = OutputExodusReader(True,0.2,data_range='last')
data_list = herd.read_results_para_generic(reader)
print(data_list[0].data_sets[-1])
#data_list[0].data_sets[-1].plot(scalars='eyy')
# %%
c = CostFunction(reader,[maximise_stress,maximise_stress_deviation],2.16E7)

costs = np.array(c.evaluate_parallel(data_list))
F = []
for i in range(costs.shape[1]):
    F.append(costs[:,i])
# %%
maximise_stress(data_list[0],2.16E7)
# %%
def maximise_stress(data,endtime):
    if data is None:
        return 1E6
    if int(data._time[-1]) != endtime:
        return 1E6
    
    return -1*np.nanmax(np.array(data.data_sets[-1]['eyy']))
# %%
T = ExodusReader('/home/rspencer/pyfemop/examples/scripts/ex1_linear_elastic_out.e')
# %%
