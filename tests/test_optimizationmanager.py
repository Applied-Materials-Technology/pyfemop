#
#
#

import pytest
import numpy as np
import os

from pyfemop.optimizationmanager.optimizationmanager import MooseOptimizationRun
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder.mooseherd import MooseRunner
from mooseherder.gmshrunner import GmshRunner

from pyfemop.optimizationmanager.costfunctions import CostFunction
from pyfemop.optimizationmanager.costfunctions import min_plastic
from pyfemop.optimizationmanager.costfunctions import creep_range
from pymoo.termination import get_termination

from pycoatl.spatialdata.importmoose import moose_to_spatialdata


def test_class_init():

    # Setup MOOSE
    moose_dir = '/home/rspencer/moose'
    moose_app_dir = '/home/rspencer/proteus'
    moose_app_name = 'proteus-opt'
    moose_input = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa.i'

    moose_modifier = InputModifier(moose_input,'#','')
    moose_runner = MooseRunner(moose_dir,moose_app_dir,moose_app_name)
    moose_vars = [moose_modifier.get_vars()]

    # Setup Gmsh
    gmsh_path = '/home/rspencer/src/gmsh/bin/gmsh'#os.path.join(user_dir,'moose-workdir/gmsh/bin/gmsh')
    gmsh_input = '/home/rspencer/mtgo/data/gmsh_script_3d_gpa.geo'

    gmsh_runner = GmshRunner(gmsh_path)
    gmsh_runner.set_input_file(gmsh_input)
    gmsh_modifier = InputModifier(gmsh_input,'//',';')

    # Start the herd and create working directories
    herd = MooseHerd(moose_runner,moose_modifier,gmsh_runner,gmsh_modifier)
    herd.set_base_dir('examples/')
    herd.clear_dirs()
    herd.create_dirs()
    
    algorithm = NSGA2(
    pop_size=8,
    n_offsprings=8,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True,
    save_history = True
    )
    termination = get_termination("n_gen", 40)
    #reader = OutputExodusReader(False)
    c = CostFunction(moose_to_spatialdata,[min_plastic,creep_range],2.16E7)
    bounds  = {'p0' : [1,2],'p1' : [0.5,1.5],'p2' : [0.25,1.25]}
    #(np.array([1E-3,1E-3,1E-3]),np.array([2.5E-3,2.5E-3,2.5E-3]))

    mor = MooseOptimizationRun('TestInit',algorithm,termination,herd,c,bounds)
    mor.backup()
    assert mor._n_obj ==2
    assert mor._n_var ==3
    assert mor._problem.xl == pytest.approx([1,0.5,0.25])
    assert mor._problem.xu == pytest.approx([2,1.5,1.25])
"""
def test_class_backup():


    moose_dir = '/home/rspencer/moose'
    app_dir = '/home/rspencer/proteus'
    app_name = 'proteus-opt'

    input_file = 'examples/creep_mesh_test_dev.i'

    geo_file = '/home/rspencer/mooseherder/data/gmsh_script_3d.geo'

    input_modifier = InputModifier(geo_file,'//',';')

    herd = MooseHerd(input_file,moose_dir,app_dir,app_name,input_modifier)
    herd.clear_dirs()
    herd.create_dirs(one_dir=False)
    herd.para_opts(n_moose=8,tasks_per_moose=1,threads_per_moose=1)
    
    algorithm = NSGA2(
    pop_size=8,
    n_offsprings=8,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True,
    save_history = True
    )
    termination = get_termination("n_gen", 40)
    c = CostFunction([min_plastic,creep_range])
    bounds  =(np.array([1E-3,1E-3,1E-3]),np.array([2.5E-3,2.5E-3,2.5E-3]))

    mor = MooseOptimizationRun('Test Init 1',algorithm,termination,herd,c,bounds)
    mor.backup()
    assert os.path.exists('examples/Test_Init_1.pickle')

    mor = MooseOptimizationRun('Test.Init.2',algorithm,termination,herd,c,bounds)
    mor.backup()
    assert os.path.exists('examples/Test_Init_2.pickle')

    mor = MooseOptimizationRun('Test.Init 3',algorithm,termination,herd,c,bounds)
    mor.backup()
    assert os.path.exists('examples/Test_Init_3.pickle')
 
    os.remove('examples/Test_Init_1.pickle')
    os.remove('examples/Test_Init_2.pickle')
    os.remove('examples/Test_Init_3.pickle')
"""