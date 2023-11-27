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

from mtgo.optimizationmanager.dummysolver import dummy_solve
from mtgo.optimizationmanager.dummysolver import dummy_solve_moo
from mtgo.optimizationmanager.dummysolver import sphere
from mtgo.optimizationmanager.dummysolver import rastigrin
from mtgo.optimizationmanager.dummysolver import rosen

from mtgo.optimizationmanager.costfunctions import CostFunction
from mtgo.optimizationmanager.costfunctions import min_plastic
from mtgo.optimizationmanager.costfunctions import creep_range

from mooseherder.mooseherd import MooseHerd

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
#%%

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



problem = Problem(n_var=2,
                  n_obj=2,
                  xl=np.array([-2,-2]),
                  xu=np.array([2,2]))


algorithm = NSGA2(
    pop_size=8,
    n_offsprings=10,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True,
    save_history = True
)

termination = get_termination("n_gen", 40)

algorithm.setup(problem,termination=termination)

for n_gen in range(40):
    # Ask for the next solution to be implemented
    pop = algorithm.ask()
    
    #Get parameters
    x = pop.get("X")
    #print(x)
    #print(x[0,1])

    F=dummy_solve_moo(x)

    static = StaticProblem(problem,F=F)
    Evaluator().eval(static,pop)

    algorithm.tell(infills=pop)
    print(algorithm.n_gen)

res = algorithm.result()
X = res.X
F = res.F


# %%
#plt.scatter(X[:,0],X[:,1])
plt.scatter(F[:,0],F[:,1])
# %%
