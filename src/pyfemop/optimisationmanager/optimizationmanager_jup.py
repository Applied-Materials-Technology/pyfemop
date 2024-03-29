# %%
# Intending to use Pymoo to optimize. 
#

import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import Problem
from pymoo.problems.static import StaticProblem
from pymoo.core.evaluator import Evaluator
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.termination import get_termination
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.optimize import minimize

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling

from pyfemop.optimisationmanager.dummysolver import dummy_solve
from pyfemop.optimisationmanager.dummysolver import dummy_solve_moo
from pyfemop.optimisationmanager.dummysolver import sphere
from pyfemop.optimisationmanager.dummysolver import rastigrin
from pyfemop.optimisationmanager.dummysolver import rosen

from pyfemop.optimisationmanager.costfunctions import CostFunction
from pyfemop.optimisationmanager.costfunctions import min_plastic
from pyfemop.optimisationmanager.costfunctions import creep_range

from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder.outputreader import output_csv_reader

from pymoo.visualization.heatmap import Heatmap
import pickle

# First step is to define a problem. 
#%%
class SphereProblem(Problem):

    def __init__(self):
        super().__init__(n_var=10,n_obj=1)
    
    def _evaluate(self, x, out, *args, **kwargs):
        # Some code here to run MOOSE in parallel I guess
        # For now it's just a spherical function to test
        out["F"] = np.sum((x-0.5)**2,axis=1)

problem = SphereProblem()
problem.n_var = 10
problem.n_obj = 1
xl = np.zeros(10)
xl = xl-0.5
xu = np.zeros(10)
xu = xu + 0.5
problem.xl = xl
problem.xu = xu
# Initialise an algorithm
algorithm = PSO(pop_size=11)
#termination = get_termination("n_gen",15)
termination = DefaultMultiObjectiveTermination(
    n_max_gen = 150

)

res = minimize(problem,algorithm,termination,save_history=True)

print(res.X)
print(res.F)

hist = res.history
n_evals = []
hist_F = []

for algo in hist:
    n_evals.append(algo.evaluator.n_eval)
    hist_F.append(algo.opt.get("F"))
#%% Dummy problem

class DummyProblem(Problem):

    def __init__(self):
        super().__init__(n_var=10,n_obj=1)
    
    def _evaluate(self, x, out, *args, **kwargs):
        # Some code here to run MOOSE in parallel I guess
        # For now it's just a spherical function to test
        
        out["F"] = dummy_solve(x,rosen)

problem = DummyProblem()
problem.n_var = 10
problem.n_obj = 1
xl = np.zeros(10)
xl = xl-5
xu = np.zeros(10)
xu = xu + 5
problem.xl = xl
problem.xu = xu

res = minimize(problem,algorithm,termination,save_history=True)

print(res.X)
print(res.F)

hist = res.history
n_evals = []
hist_F = []

for algo in hist:
    n_evals.append(algo.evaluator.n_eval)
    hist_F.append(algo.opt.get("F"))

plt.plot(n_evals,np.log(np.ravel(hist_F)))


# %%
class MyProblem(Problem):

    def __init__(self):
        super().__init__(n_var=2,
                         n_obj=2,
                         xl=np.array([-2,-2]),
                         xu=np.array([2,2]))

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = dummy_solve_moo(x)
        #out["G"] = [g1, g2]


problem = MyProblem()
algorithm = NSGA2(
    pop_size=40,
    n_offsprings=10,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True
)
termination = get_termination("n_gen", 40)
res = minimize(problem,
               algorithm,
               termination,
               seed=1,
               save_history=True,
               verbose=True)

X = res.X
F = res.F

# %%
class TestProblem(Problem):

    def __init__(self):
        super().__init__(n_var=3,
                         n_obj=2,
                         xl=np.array([1E-3,1E-3,1E-3]),
                         xu=np.array([2.5E-3,2.5E-3,2.5E-3]))

    def _evaluate(self, x, out, *args, **kwargs):

        
        #Run 
        
        # Read
        filename = '/home/rspencer/mooseherder/examples/creep_mesh_test_dev_out.csv'
        data = output_csv_reader(filename)
        # Calculate
        c = CostFunction(data,[min_plastic,creep_range])
        out["F"] = c(data)
        #out["G"] = [g1, g2]


problem = TestProblem()
algorithm = NSGA2(
    pop_size=8,
    n_offsprings=10,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True
)
termination = get_termination("n_gen", 1)
res = minimize(problem,
               algorithm,
               termination,
               seed=1,
               save_history=True,
               verbose=True)

X = res.X
F = res.F

#%% Problem independent way 



problem = Problem(n_var=3,
                  n_obj=2,
                  xl=np.array([1E-3,1E-3,1E-3]),
                  xu=np.array([2.5E-3,2.5E-3,2.5E-3]))


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

algorithm.setup(problem,termination=termination)

moose_dir = '/home/rspencer/moose'
app_dir = '/home/rspencer/proteus'
app_name = 'proteus-opt'

input_file = 'examples/creep_mesh_test_dev.i'

geo_file = '/home/rspencer/mooseherder/data/gmsh_script_3d.geo'

input_modifier = InputModifier(geo_file,'//',';')
#input_modifier = InputModifier(input_file,'#','')
# Start the herd and create working directories
herd = MooseHerd(input_file,moose_dir,app_dir,app_name,input_modifier)
herd.clear_dirs()
herd.create_dirs(one_dir=False)
herd.para_opts(n_moose=8,tasks_per_moose=1,threads_per_moose=1)

for n_gen in range(5):
    # Ask for the next solution to be implemented
    pop = algorithm.ask()
    
    #Get parameters
    x = pop.get("X")
    #print(x)
    #Run moose for all x.
    #Moose herder needs list of dicts. With correctly named parameters. 
    para_vars = list()
    for i in range(x.shape[0]):
        para_vars.append({'p0':x[i,0],'p1':x[i,1],'p2':x[i,2]})
    print(para_vars)
    
    herd.run_para(para_vars)
    print('Run time = '+str(herd._run_time)+' seconds')

    # Read in moose results and get cost. 
    data_list = herd.read_results(output_csv_reader,'csv')
    output_values = []
    for data in data_list:
        c = CostFunction(data,[min_plastic,creep_range])
        output_values.append(c.evaluate())
    # Format of f needs to be list of len (n_obj) with arrays of len(num_parts)
    costs = np.array(output_values)
    F = []
    for i in range(costs.shape[1]):
        F.append(costs[:,i])
    print(F)

    static = StaticProblem(problem,F=F)
    Evaluator().eval(static,pop)

    algorithm.tell(infills=pop)
    print(algorithm.n_gen)
    #herd.clear_dirs()

res = algorithm.result()
X = res.X
S = res.F



# %%
plt.scatter(X[:,0],X[:,1])
#plt.scatter(S[:,0],S[:,1])
# %%
filename = '/home/rspencer/mooseherder/examples/creep_mesh_test_dev_out.csv'
od = []
od.append(output_csv_reader(filename))
od.append(output_csv_reader(filename))
od.append(output_csv_reader(filename))
print(od)
ov = []
for data in od:
    c = CostFunction(data,[min_plastic,creep_range])
    ov.append(c.evaluate())
print(ov)

# %%
#Convert to numpy array first
costs = np.array(ov)
F = []
for i in range(costs.shape[1]):
    F.append(costs[:,i])

print(F)
# %% Get some history
hist = res.history
n_evals = []
hist_F = []

for algo in hist:
    n_evals.append(algo.evaluator.n_eval)
    hist_F.append(algo.opt.get("F"))

# %% Try to visualise
Heatmap().add(S).show()

# %%

class MooseOptimizationRun():

    def __init__(self,algorithm,herd,cost_function,bounds):
        """Class to contain everything needed for an optimization run 
        with moose. Should be pickle-able.

        Args:
            algorithm (pymoo algorithm): Choice of algorithm for the optimization
            herd (MooseHerd): MooseHerd instance for the run.
            costfunction (CostFunction): CostFunction instance.
            bounds (tuple): 2-tuple containing lower and upper bounds as arrays
        """
        self._algorithm = algorithm
        self._herd = herd
        self._cost_function = cost_function
        self._n_var = len(self._herd._modifier._vars)
        self._n_obj = self._cost_function.n_obj
        self._bounds = bounds

        self._problem = Problem(n_var=self._n_var,
                  n_obj=self._n_obj,
                  xl=self._bounds[0],
                  xu=self._bounds[1])

