#
#
#

import pytest
import numpy as np

from mtgo.optimizationmanager.optimizationmanager import MooseOptimizationRun
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier

from mtgo.optimizationmanager.costfunctions import CostFunction
from mtgo.optimizationmanager.costfunctions import min_plastic
from mtgo.optimizationmanager.costfunctions import creep_range
from pymoo.termination import get_termination

def test_class_init():

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

    mor = MooseOptimizationRun(algorithm,termination,herd,c,bounds)
    
    assert mor._n_obj ==2
    assert mor._n_var ==3
    assert mor._problem.xl == pytest.approx([1E-3,1E-3,1E-3])
    assert mor._problem.xu == pytest.approx([2.5E-3,2.5E-3,2.5E-3])