#
# Some methods for reading in an building cost functions. 
#


class CostFunction():

    def __init__(self,functions,endtime):
        """_summary_

        Args:
            data (dict): Data used to calculated cost functions
            functions (list): List of defined functions using the values in data.
        """
        #self._data = data
        self._functions = functions
        self.n_obj = len(self._functions)
        self._endtime = endtime

    def evaluate(self,data):
        """Calculate the cost of each function, to pass back to pymoo
        
        Returns:
            list: Costs for each function 
        """
        f= []
        for function in self._functions:
            f.append(function(data,self._endtime))
        return f

# Define some functions to use as trials

def min_plastic(data,endtime):
    # Maybe add a check that time == 100 to ensure run completed.
    if data["time"] == endtime:
        cost = data['max_plas_strain']
    else:
        cost = 1E6
    return cost

def creep_range(data,endtime):
    if data["time"] == endtime:
        cost = -1*(data['max_creep_strain']-data['min_creep_strain'])
    else:
        cost = 1E6
    return cost

def max_stress(data,endtime):
    if data["time"] == endtime:
        cost = -1*(data['max_stress'])
    else:
        cost = 1E6
    return cost

def avg_creep(data,endtime):
    if data["time"] == endtime:
        cost = -1*(data['avg_creep'])
    else:
        cost = 1E6
    return cost