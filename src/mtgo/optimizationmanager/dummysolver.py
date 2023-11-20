#
# Methods to act as a dummy solver
# I.e. produce fake FE costs as if the solver and cost functions had been evaluated.

import numpy as np

def dummy_solve(x, fun):
    """Produces costs as if from an FE solve

    Args:
        x (float array): Float to be passed to function
        fun (function): function to be optimized

    Returns:
        float: simulated cost 
    """
    c = np.empty(x.shape[0])
    for i in range(len(c)):
        c[i] = fun(x[i])
    return c

def dummy_solve_moo(x):
    """Produces costs as if from an FE solve

    Args:
        x (float array): Float to be passed to function
        fun (function): function to be optimized

    Returns:
        float: simulated cost 
    """
    f1 = np.empty(x.shape[0])
    f2 = np.empty(x.shape[0])
    for i in range(len(f1)):
        f1[i] = 100 * (x[0]**2 + x[1]**2)
        f2[i] = (x[0]-1)**2 + x[1]**2
    return [f1,f2]

def rosen(x):
    """
    The Rosenbrock function
    Has global minima at (1,1,...,1)    
    """
    return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)

def sphere(x):
    """
    Spherical Function (global minimum at 0,0,...,0)
    Search space -inf<xi<inf
    """
    return np.sum(x**2)

def rastigrin(x):
    """
    Rastigrin function (global minimum at 0,0,...,0)
    Search space -5.12<xi<5.12
    """
    s = np.sum(x**2-10*np.cos(2*np.pi*x))
    return 10*len(x)+s

