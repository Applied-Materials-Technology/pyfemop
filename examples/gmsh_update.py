#
# Example of updating the gmsh file in data with some new parameters
#

from mtgo.filemanager import InputModifier
from mtgo.gmshutils import RunGmsh

input_file = '/home/rspencer/mtgo/data/gmsh_script.geo'
im = InputModifier(input_file,'//',';')

new_vars = {'p0':2.E-3,'p1':3.E-3,'p2':1.E-3}

RunGmsh(input_file)

im.update_vars(new_vars)
output_file = '/home/rspencer/mtgo/data/gmsh_script_mod.geo'
im.write_file(output_file)

RunGmsh(output_file)

