#
# Some methods for reading in an building cost functions. 
#
import multiprocessing as mp
import numpy as np

class CostFunction():

    def __init__(self,reader,objective_functions,endtime,ineq_constraints=None,eq_constraints=None):
        """_summary_

        Args:
            data (dict): Data used to calculated cost functions
            functions (list): List of defined functions using the values in data.
        """
        #self._data = data
        self._reader = reader
        self._objective_functions = objective_functions
        self._ineq_constraints = ineq_constraints
        self._eq_constraints = eq_constraints
        self.n_obj = len(self._objective_functions)
        if ineq_constraints is not None:
            self.n_ieq_constraints = len(ineq_constraints)
        else: 
            self.n_ieq_constraints =0

        if eq_constraints is not None:
            self.n_eq_constraints = len(eq_constraints)
        else: 
            self.n_eq_constraints =0
        self._endtime = endtime

    def evaluate_objectives(self,data):
        """Calculate the cost of each function, to pass back to pymoo
        
        Returns:
            list: Costs for each function 
        """
        f= []
        for function in self._objective_functions:
            f.append(function(data,self._endtime))
        return f
    
    def evaluate_constraints(self,data):
        """Calculate the cost of each function, to pass back to pymoo
        
        Returns:
            list: Costs for each function 
        """
        g= []
        for function in self._constraints:
            g.append(function(data,self._endtime))
        return g
    
    def evaluate_parallel(self,data_list):
        #Evaluate all objectives and constraints in parallel.
        n_threads = len(data_list)

        with mp.Pool(n_threads) as pool:
            processes = []
            for data in data_list:
                processes.append(pool.apply_async(self.evaluate_objectives, (data,))) # tuple is important, otherwise it unpacks strings for some reason
            f_list=[pp.get() for pp in processes]
        
        return f_list


# Define some functions to use as trials

def objective_function(data,endtime):
    """Parent class to be overwritten by others

    Args:
        data (dict): Should be dict, unless the model didn't run
        endtime (int): End time of the simulation 
    """
    

def min_plastic(data,endtime):
    # Maybe add a check that time == 100 to ensure run completed.
    try: 
        if data["time"] == endtime:
            cost = data['max_plas_strain']
        else:
            cost = 1E6
    except(TypeError):
        print('Suspect model did not run')
        cost = 1E6
    return cost

def creep_range(data,endtime):
    if data["time"] == endtime:
        cost = -1*(data['max_creep_strain']-data['min_creep_strain'])
    else:
        cost = 1E6
    return cost

def max_stress(data,endtime):
    try:
        if data["time"] == endtime:
            cost = -1*(data['max_stress'])
        else:
            cost = 1E6
    except(TypeError):
        print('Suspect model did not run')
        cost = 1E6
    return cost

def avg_creep(data,endtime):
    try:
        if data["time"] == endtime:
            cost = -1*(data['avg_creep'])
        else:
            cost = 1E6
    except(TypeError):
        print('Suspect model did not run')
        cost = 1E6
    return cost

def maximise_stress(data,endtime):
    if data is None:
        return 1E6
    if int(data._time[-1]) != endtime:
        return 1E6
    
    return -1*np.max(data.data_sets[-1]['stress_yy'])

def maximise_stress_deviation(data,endtime):
    if data is None:
        return 1E6
    if int(data._time[-1]) != endtime:
        return 1E6
    
    return -1*np.std(data.data_sets[-1]['stress_yy'])


