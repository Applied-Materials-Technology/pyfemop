#
# To test run the optimization manager.
#
#%% Imports
import numpy as np

from mtgo.optimizationmanager.optimizationmanager import MooseOptimizationRun
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier

from mtgo.optimizationmanager.costfunctions import CostFunction
from mtgo.optimizationmanager.costfunctions import min_plastic
from mtgo.optimizationmanager.costfunctions import creep_range
from mtgo.optimizationmanager.costfunctions import max_stress
from mtgo.optimizationmanager.costfunctions import avg_creep
from pymoo.termination import get_termination
import pickle
from matplotlib import pyplot as plt
#%% Baseline run
moose_dir = '/home/rspencer/moose'
app_dir = '/home/rspencer/proteus'
app_name = 'proteus-opt'

input_file = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa.i'

geo_file = '/home/rspencer/mtgo/data/gmsh_script_3d_gpa_xy.geo'

input_modifier = InputModifier(geo_file,'//',';')

herd = MooseHerd(input_file,moose_dir,app_dir,app_name,input_modifier)
herd.clear_dirs()
herd.create_dirs(one_dir=False)
herd.para_opts(n_moose=8,tasks_per_moose=1,threads_per_moose=1)

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
c = CostFunction([min_plastic,max_stress],2.16E7)
#c = CostFunction([avg_creep,max_stress],2.16E7)
#bounds  =(np.array([1.,1.,1.]),np.array([2.5,2.5,2.5]))
bounds  =(np.array([0.35,-0.5]),np.array([0.8,0.5]))

mor = MooseOptimizationRun('Run_Stress_plastic_hiload2_gpa_alt',algorithm,termination,herd,c,bounds)

#%%
mor.run(14)



#%% Test pickling
pickle_path = '/home/rspencer/mtgo/examples/Run_Stress_plastic_hiload_gpa.pickle'
with open(pickle_path,'rb') as f:
    morl = pickle.load(f,encoding='latin-1')



#%% Test another run
mor.run(10)

# %%
S = mor._algorithm.result().F 
X = mor._algorithm.result().X
#for i in range(X.shape[0]):
#   plt.plot([X[i,0],X[i,1],X[i,2]],[5,0,-5])
for i in range(X.shape[0]):
    plt.plot([2.5,X[i,1],2.5],[-10,X[i,0],10])
#%%
plt.scatter(S[:,0],S[:,1])
# %%
mor.run_optimal([0,1,2])
# %%
