#
#
# Import all necessary packages

import numpy as np
from matplotlib import pyplot as plt
from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun


print('------------------------------------------------')
print('                  Example-3                     ')
print('              Run Visualisation           ')
print('------------------------------------------------')

# Import example 1 run
mor = MooseOptimisationRun.restore_backup('examples/ex1_Linear_Elastic.pickle')

# Get algorithm history
hist = mor._algorithm.history
n_evals = []             # corresponding number of function evaluations\
hist_F = []              # the objective space values in each generation
hist_X = []
for algo in hist:

    # store the number of function evaluations
    n_evals.append(algo.evaluator.n_eval)
    hist_F.append(algo.opt[0].F)
    hist_X.append(algo.opt[0].X)

#print(n_evals)
#print(hist_F)

fig = plt.figure()
ax = fig.add_subplot()
ax.plot(n_evals,hist_F)
ax.set_xlabel('Models Run')
ax.set_ylabel('Residual')
fig.savefig('examples/convergence.png')

print('Plot save to: examples/convergence.png')



