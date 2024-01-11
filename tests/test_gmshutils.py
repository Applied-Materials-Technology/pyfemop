#
#
#

import pytest
from pyfemop.gmshutils import RunGmsh

def test_run_file_exception():
    wrong_extension ='/home/rspencer/mtgo/data/dummy.i'
    with pytest.raises(FileNotFoundError):
        RunGmsh(wrong_extension)
    missing_file = '/home/rspencer/mtgo/data/dummy.geo'
    with pytest.raises(FileNotFoundError):
        RunGmsh(missing_file)


#def test_gmsh_run():
#    in_file = '/home/rspencer/mtgo/data/gmsh_script.geo'
#    RunGmsh(in_file)