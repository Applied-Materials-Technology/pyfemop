#
#
#

import pytest
import numpy as np

from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooseherd import MooseRunner
from mooseherder.gmshrunner import GmshRunner

from pyfemop.optimisationmanager.costfunctions import CostFunction
from pyfemop.optimisationmanager.costfunctions import min_plastic
from pyfemop.optimisationmanager.costfunctions import ObjectiveFunctionBase
from pymoo.termination import get_termination

#from pycoatl.spatialdata.importmoose import moose_to_spatialdata

from pymoo.algorithms.soo.nonconvex.ga import GA
def test_moose_only():
    # Setup MOOSE Parameters
    moose_dir = '/home/rspencer/moose'
    moose_app_dir = '/home/rspencer/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = '/home/rspencer/pyfemop/examples/scripts/ex1_linear_elastic.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_vars = [moose_modifier.get_vars()]

    herd = MooseHerd(moose_runner,moose_modifier)

    # Create algorithm. Use SOO GA as only one objective
    algorithm = GA(
    pop_size=12,
    eliminate_duplicates=True,
    save_history = True
    )
    # Set termination criteria for optimisation
    termination = get_termination("n_gen", 10)

    # Define an objective function
    def displacement_match(data):
        # Want to get the displacement at final timestep to be close to 0.0446297
        return np.abs(np.max(data)-0.0446297)

    # Instance cost function
    c = CostFunction(None,[displacement_match],None)

    # Assign bounds
    bounds  = {'e_modulus' : [0.5E9,2E9]}

    # Create run
    mor = MooseOptimisationRun('Test_MOOSE_Only',algorithm,termination,herd,c,bounds)

    assert mor._n_obj ==1
    assert mor._n_var ==1
    assert mor._problem.xl == pytest.approx([0.5E9])
    assert mor._problem.xu == pytest.approx([2E9])
    assert mor._moose_params == ['e_modulus']
    assert mor._moose_opt_params == ['e_modulus']
    assert mor._gmsh_opt_params == []
    assert mor._mod_gmsh == False
    assert mor._mod_moose == True

def test_gmsh_only():

    # Setup MOOSE Parameters
    moose_dir = '/home/rspencer/moose'
    moose_app_dir = '/home/rspencer/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = '/home/rspencer/pyfemop/examples/scripts/ex1_linear_elastic.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_vars = [moose_modifier.get_vars()]

    # Setup Gmsh
    gmsh_path = '/home/rspencer/src/gmsh/bin/gmsh'
    gmsh_input = '/home/rspencer/pyfemop/examples/scripts/gmsh_3P_spline_3d.geo'

    gmsh_runner = GmshRunner(gmsh_path)
    gmsh_runner.set_input_file(gmsh_input)
    gmsh_modifier = InputModifier(gmsh_input,'//',';')

    herd = MooseHerd(moose_runner,moose_modifier,gmsh_runner,gmsh_modifier)

    # Create algorithm. Use SOO GA as only one objective
    algorithm = GA(
    pop_size=12,
    eliminate_duplicates=True,
    save_history = True
    )
    # Set termination criteria for optimisation
    termination = get_termination("n_gen", 10)

    # Define an objective function
    def displacement_match(data):
        # Want to get the displacement at final timestep to be close to 0.0446297
        return np.abs(np.max(data)-0.0446297)

    # Instance cost function
    c = CostFunction(None,[displacement_match],None)

    # Assign bounds
    bounds  = {'p0' : [1.5,2.5],'p1' : [1.5,2.5]}

    # Create run
    mor = MooseOptimisationRun('Test_Gmsh_Only',algorithm,termination,herd,c,bounds)

    assert mor._moose_params == ['e_modulus']
    assert mor._moose_opt_params == []
    assert all([x in mor._gmsh_params for x in ['p0','p1','p2']])
    assert all([x in mor._gmsh_opt_params for x in ['p0','p1']])
    assert mor._mod_gmsh == True
    assert mor._mod_moose == False

    mor.run_test(1)

def test_both():

    # Setup MOOSE Parameters
    moose_dir = '/home/rspencer/moose'
    moose_app_dir = '/home/rspencer/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = '/home/rspencer/pyfemop/examples/scripts/ex1_linear_elastic.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_vars = [moose_modifier.get_vars()]

    # Setup Gmsh
    gmsh_path = '/home/rspencer/src/gmsh/bin/gmsh'
    gmsh_input = '/home/rspencer/pyfemop/examples/scripts/gmsh_3P_spline_3d.geo'

    gmsh_runner = GmshRunner(gmsh_path)
    gmsh_runner.set_input_file(gmsh_input)
    gmsh_modifier = InputModifier(gmsh_input,'//',';')

    herd = MooseHerd(moose_runner,moose_modifier,gmsh_runner,gmsh_modifier)

    # Create algorithm. Use SOO GA as only one objective
    algorithm = GA(
    pop_size=12,
    eliminate_duplicates=True,
    save_history = True
    )
    # Set termination criteria for optimisation
    termination = get_termination("n_gen", 10)

    # Define an objective function
    def displacement_match(data):
        # Want to get the displacement at final timestep to be close to 0.0446297
        return np.abs(np.max(data)-0.0446297)

    # Instance cost function
    c = CostFunction(None,[displacement_match],None)

    # Assign bounds
    bounds  = {'e_modulus':[0.5e9,2e9],'p0' : [1.5,2.5],'p1' : [1.5,2.5]}

    # Create run
    mor = MooseOptimisationRun('Test_Both',algorithm,termination,herd,c,bounds)

    assert mor._moose_params == ['e_modulus']
    assert mor._moose_opt_params == ['e_modulus']
    assert all([x in mor._gmsh_params for x in ['p0','p1','p2']])
    assert all([x in mor._gmsh_opt_params for x in ['p0','p1']])
    assert mor._mod_gmsh == True
    assert mor._mod_moose == True


def test_pickling():

    # Setup MOOSE Parameters
    moose_dir = '/home/rspencer/moose'
    moose_app_dir = '/home/rspencer/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = '/home/rspencer/pyfemop/examples/scripts/ex1_linear_elastic.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_vars = [moose_modifier.get_vars()]

    herd = MooseHerd(moose_runner,moose_modifier)

    # Create algorithm. Use SOO GA as only one objective
    algorithm = GA(
    pop_size=12,
    eliminate_duplicates=True,
    save_history = True
    )
    # Set termination criteria for optimisation
    termination = get_termination("n_gen", 10)

    # Define an objective function
    class stress_function(ObjectiveFunctionBase):
        def calculate(data,endtime):
            cur_stress = data['vonmises_stress']
            if cur_stress is not None:
                cost = np.abs(np.max(cur_stress)-6.0226E7)
            else:
                cost = 1E10                        
            return cost

    # Instance cost function
    c = CostFunction(None,[stress_function],None)

    # Assign bounds
    bounds  = {'e_modulus' : [0.5E9,2E9]}

    # Create run
    mor = MooseOptimisationRun('Test_Pickling',algorithm,termination,herd,c,bounds)
    mor.backup()
    
    restore = MooseOptimisationRun.restore_backup(mor.backup_path)

    assert restore._n_obj ==1
    assert restore._n_var ==1
    assert restore._problem.xl == pytest.approx([0.5E9])
    assert restore._problem.xu == pytest.approx([2E9])
    assert restore._moose_params == ['e_modulus']
    assert restore._moose_opt_params == ['e_modulus']
    assert restore._gmsh_opt_params == []
    assert restore._mod_gmsh == False
    assert restore._mod_moose == True