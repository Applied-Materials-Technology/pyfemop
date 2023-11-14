#
# Intending to use Pymoo to optimize. 
#

import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import Problem
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.termination import get_termination
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.optimize import minimize

# First step is to define a problem. 

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
algorithm = PSO(pop_size=10)
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


plt.plot(n_evals,np.ravel(np.array(hist_F)))




