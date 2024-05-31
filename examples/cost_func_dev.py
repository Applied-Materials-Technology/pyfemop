#%%
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.soo.nonconvex.nelder import NelderMead
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.problems.static import StaticProblem
from pymoo.core.evaluator import Evaluator
from pymoo.optimize import minimize
from matplotlib import pyplot as plt

#%%

class QuadraticProblem(ElementwiseProblem):

    def __init__(self):
        super().__init__(n_var=2,n_obj=1,xl=-5,xu=5)

    def _evaluate(self,x,out,*args,**kwargs):
        xvals = np.linspace(0,1)
        func = 3 + x[0]*xvals + xvals*(x[1]**2)
        out["F"] = -np.sum(func/np.max(func))

algorithm = NelderMead()#PSO(pop_size=30)

res=minimize(QuadraticProblem(),algorithm,seed=1,save_history=True,verbose=True)


print(res.X)
print(res.F)
x = res.X
xvals = np.linspace(0,1)
func = 3 + x[0]*xvals + xvals*(x[1]**2)
plt.plot(xvals,func)
# %%
x= [1,4]
xvals = np.linspace(0,1)
func = 3 + x[0]*xvals + xvals*(x[1]**2)
print(np.sum(func/np.max(func)))

# %%
