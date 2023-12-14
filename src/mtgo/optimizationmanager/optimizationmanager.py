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
from mooseherder.inputmodifier import InputModifier
from mooseherder.outputreader import output_csv_reader

from pymoo.visualization.heatmap import Heatmap
import pickle

class MooseOptimizationRun():

    def __init__(self,name,algorithm,termination,herd,cost_function,bounds):
        """Class to contain everything needed for an optimization run 
        with moose. Should be pickle-able.

        Args:
            name (str) : string to name the run.
            algorithm (pymoo algorithm): Choice of algorithm for the optimization
            termination (pymoo termination): Termination criteria for the algorithm
            herd (MooseHerd): MooseHerd instance for the run.
            costfunction (CostFunction): CostFunction instance.
            bounds (tuple): 2-tuple containing lower and upper bounds as arrays
        """
        self._name = name
        self._algorithm = algorithm
        self._herd = herd
        self._cost_function = cost_function
        self._n_var = len(self._herd._modifier._vars)
        self._n_obj = self._cost_function.n_obj
        self._bounds = bounds
        self._termination = termination
        self._reader = cost_function._reader # Data reader 

        self._problem = Problem(n_var=self._n_var,
                  n_obj=self._n_obj,
                  xl=self._bounds[0],
                  xu=self._bounds[1])
        
        # Setup algorithm
        self._algorithm.setup(self._problem,termination=termination)

    def backup(self):
        """Create a pickle dump of the class instance.
        """
        pickle_path = self._herd._input_dir + '/' + self._name.replace(' ','_').replace('.','_') + '.pickle'
        #print(pickle_path)
        with open(pickle_path,'wb') as f:
            pickle.dump(self,f,pickle.HIGHEST_PROTOCOL)


    def run(self,num_its):
        """Run the optimization for n_its number of generations.
        Only if the algorithm hasn't terminated.

        Args:
            num_its (int): _description_
        """
        for n_gen in range(num_its):
            #Check if termination criteria has been met. 
            if not self._algorithm.has_next():
                # Kill the loop if the algorithm has terminated.
                break
            print('*****Running Optimization Generation {}*****'.format(self._algorithm.n_gen))
            # Ask for the next solution to be implemented
            self._herd.clear_dirs()
            self._herd.create_dirs(one_dir=False)
            pop = self._algorithm.ask()
            
            #Get parameters
            x = pop.get("X")

            #Run moose for all x.
            #Moose herder needs list of dicts. With correctly named parameters. 
            para_vars = list()
            para_names = self._herd._modifier.get_var_keys()
            for i in range(x.shape[0]):
                para_dict = dict()
                for j in range(len(para_names)):
                    para_dict[para_names[j]] = x[i,j]
                para_vars.append(para_dict)
                   
            self._herd.run_para(para_vars)
            print('Run time = '+str(self._herd._run_time)+' seconds')

            # Read in moose results and get cost. 
            print('*****Reading Data*****')
            data_list = self._herd.read_results_para(self._reader)
            
            #output_values = []
            #for data in data_list:
            #    c = self._cost_function.evaluate_objectives(data)
            #    output_values.append(c)
            # Format of f needs to be list of len (n_obj) with arrays of len(num_parts)
            #costs = np.array(output_values)
            costs = np.array(self._cost_function.evaluate_parallel(data_list))
            F = []
            for i in range(costs.shape[1]):
                F.append(costs[:,i])
            

            static = StaticProblem(self._problem,F=F)
            Evaluator().eval(static,pop)

            self._algorithm.tell(infills=pop)
            self.backup()
            print('**** Generation Complete ****')

    
    def run_optimal(self,pf_nums):
        """Run a model from the pareto front

        Args:
            pf_num (list of int): Integer of the pareto front optimum to run.
        """
        
        f = self._algorithm.result().F[pf_nums] 
        x = self._algorithm.result().X[pf_nums]
        
        print('The selected parameters are: {}'.format(x))
        print('The pareto front position is: {}'.format(f))

        # Create runner
        # Temp herder
        temp_herd = MooseHerd(self._herd.input_file,self._herd._runner.moose_dir,self._herd._runner.app_dir,self._herd._runner.app_name,self._herd._modifier)
        temp_herd.clear_dirs()
        # There's some kind of bug with create_dirs, doesn' create via para_opts
        temp_herd.create_dirs(one_dir=False,sub_dir='moose-opt')
        temp_herd.para_opts(n_moose=len(pf_nums),tasks_per_moose=1,threads_per_moose=1)
        
        para_vars = list()
        para_names = self._herd._modifier.get_var_keys()
        for i in range(x.shape[0]):
            para_dict = dict()
            for j in range(len(para_names)):
                para_dict[para_names[j]] = x[i,j]
            para_vars.append(para_dict)
        
        print('**** Running Selected Models ****')
        temp_herd.run_para(para_vars)  
        