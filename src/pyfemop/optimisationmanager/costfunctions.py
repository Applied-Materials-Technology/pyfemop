#
# Some methods for reading in an building cost functions. 
#
import multiprocessing as mp
import numpy as np

class CostFunction():

    def __init__(self,reader,objective_functions,endtime,dic_filter = False, filter_size=0.2,dic_data = None,ineq_constraints=None,eq_constraints=None):
        """Cost functions to be evaluated. 
        Now will run on .exodus output only. 

        Args:
            reader (function): Function read the data and get into whatever format. Presumably should be moose_to_spatialdata
            objective_functions (list of functions): Functions to run over data.
            endtime (float): Endtime of the simuation.
            dic_filter (bool, optional): Whether to run a DIC filter on the data. Defaults to False.
            filter_size (float, optional): Size of the filter. Defaults to 0.2.
            dic_data (SpatialData, optional): Dic data to use in costfunction maybe. Defaults to None.
            ineq_constraints (list of functions, optional): Functions describing inequality constraints. Defaults to None.
            eq_constraints (list of functions, optional): Functions describing equality constraints. Defaults to None.
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


class ObjectiveFunctionBase():
    """Base class for cost function.
    """
    def calculate(data,endtime):
        """To be overwritten, calculates cost function

        Args:
            data (dict/SpatialData): Data to be used, can be any format 
            endtime (float): Endtime of the simulation, if required

        Returns:
            float: the cost associated with this objective
        """

        return None



# Define some functions to use as trials

def objective_function(data,endtime):
    """Parent class to be overwritten by others

    Args:
        data (dict): Should be dict, unless the model didn't run
        endtime (int): End time of the simulation 
    """
    pass
    

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

def maximise_strain(data,endtime):
    if data is None:
        return 1E6
    if int(data._time[-1]) != endtime:
        return 1E6
    
    return -1*np.nanmax(np.array(data.data_sets[-1]['eyy']))

def maximise_strain_deviation(data,endtime):
    if data is None:
        return 1E6
    if int(data._time[-1]) != endtime:
        return 1E6
    
    return -1*np.nanstd(np.array(data.data_sets[-1]['eyy']))


