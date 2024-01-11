#
#
#

import pytest
from pyfemop.optimizationmanager.costfunctions import CostFunction
from pyfemop.optimizationmanager.costfunctions import min_plastic
from pyfemop.optimizationmanager.costfunctions import creep_range

from mooseherder.outputreader import output_csv_reader




def test_min_plastic():
    filename = '/home/rspencer/mooseherder/examples/creep_mesh_test_dev_out.csv'
    assert min_plastic(output_csv_reader(filename)) == pytest.approx(3.335469E-5)

def test_creep_range():
    filename = '/home/rspencer/mooseherder/examples/creep_mesh_test_dev_out.csv'
    assert creep_range(output_csv_reader(filename)) == pytest.approx(-0.005906137)

def test_costfunction():
    filename = '/home/rspencer/mooseherder/examples/creep_mesh_test_dev_out.csv'
    data = output_csv_reader(filename)

    c = CostFunction(data,[min_plastic,creep_range])
    output_values = c.evaluate()
    print(output_values)
    assert output_values[0] == pytest.approx(3.335469E-5)
    assert output_values[1] == pytest.approx(-0.005906137)

def test_costfunction():
    filename = '/home/rspencer/mtgo/examples/unconverged.csv'
    data = output_csv_reader(filename)

    c = CostFunction(data,[min_plastic,creep_range])
    output_values = c.evaluate()
    print(output_values)
    assert output_values[0] == pytest.approx(10)
    assert output_values[1] == pytest.approx(10)

