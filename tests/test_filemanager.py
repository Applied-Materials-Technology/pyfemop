#
#
#

import pytest
from pyfemop.filemanager import InputModifier

def test_inputmanager():
    input_file = '/home/rspencer/mtgo/data/gmsh_script.geo'
    im = InputModifier(input_file,'//',';')
    print(type(im.var_start))
    print(im._vars)
    assert im.var_start == 11 
    assert im.var_end == 15

    assert im._vars['p0'] == pytest.approx(1.5e-3)
    assert im._vars['p1'] == pytest.approx(1.e-3)
    assert im._vars['p2'] == pytest.approx(1.2e-3)

def test_update():
    input_file = '/home/rspencer/mtgo/data/gmsh_script.geo'
    im = InputModifier(input_file,'//',';')
    
    new_bad_dict = {'p0':3.0,'t1':40.,'p2':50.}
    new_good_dict = {'p0':2.,'p1':3.,'p2':4.}
    
    im.update_vars(new_good_dict)
    assert im._vars['p0'] == pytest.approx(2)
    assert im._vars['p1'] == pytest.approx(3)
    assert im._vars['p2'] == pytest.approx(4)

    with pytest.raises(KeyError):
        im.update_vars(new_bad_dict)

def test_write():
    input_file = '/home/rspencer/mtgo/data/gmsh_script.geo'
    im = InputModifier(input_file,'//',';')
    output_file = '/home/rspencer/mtgo/data/gmsh_script_mod.geo'
    
    new_good_dict = {'p0':2.,'p1':3.,'p2':4.}
    im.update_vars(new_good_dict)
    im.write_file(output_file)