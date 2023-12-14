#
#
# Interactive moose read tests

#%%
from mtgo.mooseutils.outputreaders import output_exodus_reader
from mtgo.mooseutils.outputreaders import OutputExodusReader
import numpy as np

# %%
efile = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa_hole_plate_out.e'
test = output_exodus_reader(efile,False)
test[-1].plot(scalars='mechanical_strain_yy',cpos='xy')
# %%
efile = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa_hole_plate_out.e'
reader = OutputExodusReader(False)
test = reader.read(efile)
test[-1].plot(scalars='mechanical_strain_yy',cpos='xy')


# %%
efile = '/home/rspencer/mtgo/examples/creep_mesh_test_dev_gpa_hole_plate_out.e'
reader = OutputExodusReader(True)
test = reader.read(efile)
test[-1].plot(scalars='eyy',cpos='xy')
# %%
