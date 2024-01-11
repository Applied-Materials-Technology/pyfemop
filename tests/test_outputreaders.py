#
#
#

import pytest
from pyfemop.mooseutils.outputreaders import output_exodus_reader

def test_ex_none():
    file = '/Doesntexist.e'
    data = output_exodus_reader(file,True,0.2,None,'last',5)
    assert data == None