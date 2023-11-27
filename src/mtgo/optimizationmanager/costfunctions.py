#
# Some methods for reading in an building cost functions. 
#


class CostFunction():

    def __init__(self,data,functions):
        """_summary_

        Args:
            data (dict): Data used to calculated cost functions
            functions (list): List of defined functions using the values in data.
        """
        self._data = data
        self._functions = functions

    def evaluate(self):
        """Calculate the cost of each function, to pass back to pymoo
        
        Returns:
            list: Costs for each function 
        """
        f= []
        for function in self._functions:
            f.append(function(self._data))
        return f

# Define some functions to use as trials

def min_plastic(data):
    return data['max_plas_strain']

def creep_range(data):
    return -1*(data['max_creep_strain']-data['min_creep_strain'])