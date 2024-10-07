#
#
# Import all necessary packages

import numpy as np

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination import get_termination
from pymoo.termination.default import DefaultMultiObjectiveTermination

from pathlib import Path
from mooseherder.mooseconfig import MooseConfig
from mooseherder.mooseherd import MooseHerd
from mooseherder.inputmodifier import InputModifier
from mooseherder import MooseRunner
from mooseherder import DirectoryManager
from mooseherder import GmshRunner

from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun
from pyfemop.optimisationmanager.optimisationmanager import OptimisationInputs
from pyfemop.optimisationmanager.costfunctions import CostFunction
from pycoatl.spatialdata.importdicedata import simdata_dice_to_spatialdata
from pycoatl.datafilters.datafilters import DiceFilter
from pycoatl.datafilters.datafilters import DiceManager
from pycoatl.datafilters.datafilters import DiceOpts

from pyvale.imagesim.imagedefopts import ImageDefOpts
from pyvale.imagesim.cameradata import CameraData

print('------------------------------------------------')
print('                  Example-4                     ')
print('              DICE Filter Checks                ')
print('------------------------------------------------')

# Setup MOOSE Config
config = {'main_path': Path.home()/ 'projects/moose',
        'app_path': Path.home() / 'projects/sloth',
        'app_name': 'sloth-opt'}

moose_config = MooseConfig(config)

save_path = Path.cwd() / 'moose-config.json'
moose_config.save_config(save_path)


moose_input = Path('/home/rspencer/pyfemop/examples/scripts/ex2_simple_geometry.i')
moose_modifier = InputModifier(moose_input,'#','')

config_path = Path.cwd() / 'moose-config.json'
moose_config = MooseConfig().read_config(config_path)

moose_runner = MooseRunner(moose_config)
moose_runner.set_run_opts(n_tasks = 1,
                        n_threads = 1,
                        redirect_out = True)

dir_manager = DirectoryManager(n_dirs=4)


# Setup Gmsh

# Setup Gmsh
gmsh_input = Path('/home/rspencer/pyfemop/examples/scripts/gmsh_2d_simple_geom.geo')
gmsh_modifier = InputModifier(gmsh_input,'//',';')

gmsh_path = Path.home() / 'src/gmsh/bin/gmsh'
gmsh_runner = GmshRunner(gmsh_path)
gmsh_runner.set_input_file(gmsh_input)

# Setup herd composition
sim_runners = [gmsh_runner,moose_runner]
input_modifiers = [gmsh_modifier,moose_modifier]

dir_manager.set_base_dir(Path('examples/'))
dir_manager.clear_dirs()
dir_manager.create_dirs()

# Start the herd and create working directories
herd = MooseHerd(sim_runners,input_modifiers,dir_manager)
#herd.set_keep_flag(False)
# Set the parallelisation options, we have 8 combinations of variables and
# 4 MOOSE intances running, so 2 runs will be saved in each working directory
herd.set_num_para_sims(n_para=8)

# Create algorithm. Use SOO GA as only one objective
algorithm = GA(
pop_size=2,
eliminate_duplicates=True,
save_history = True
)

# Set termination criteria for optimisation
#termination = get_termination("n_gen", 2)
termination = DefaultMultiObjectiveTermination(
    xtol = 1e-3,
    cvtol = 1e-3,
    ftol = 1e-3,
    period = 3,
    n_max_gen = 20
)

# Specify filter
id_opts = ImageDefOpts()
id_opts.save_path = Path.cwd()/'examples'/ 'ImDef'/ 'deformed_images'

# If the input image is just a pattern then the image needs to be masked to
# show just the sample geometry. This setting generates this image.
id_opts.mask_input_image = True
# Set this to True for holes and notches and False for a rectangle
id_opts.def_complex_geom = True

# If the input image is much larger than needed it can also be cropped to
# increase computational speed.
id_opts.crop_on = True
id_opts.crop_px = np.array([650,2000])

# Calculates the m/px value based on fitting the specimen/ROI within the camera
# FOV and leaving a set number of pixels as a border on the longest edge
id_opts.calc_res_from_fe = False
id_opts.calc_res_border_px = 10

# Set this to true to create an undeformed masked image
id_opts.add_static_ref = 'pad_disp'

print('-'*80)
print('ImageDefOpts:')
print(vars(id_opts))
print('-'*80)
print('')

# Create Camera
camera = CameraData()
# Need to set the number of pixels in [X,Y], the bit depth and the m/px

# Assume the camera has the same number of pixels as the input image unless we
# are going to crop/mask the input image
camera.num_px = id_opts.crop_px

# Based on the max grey level work out what the bit depth of the image is
camera.bits = 8

# Assume 1mm/px to start with, can update this to fit FE data within the FOV
# using the id_opts above. Or set this manually.
camera.m_per_px = 1.e-5 # Overwritten by id_opts.calc_res_from_fe = True


# Define necessary inputs
pycoatl_path = Path('/home/rspencer/pycoatl')
input_file_name = pycoatl_path/'examples/ImDef/input.xml'
mod_file_name = input_file_name.parent /'input_mod.xml'
deformed_images = pycoatl_path/'examples/ImDef/deformed_images'
subset_file =  input_file_name.parent /'subsets_roi.txt'
output_folder = input_file_name.parent /'results'
base_image = pycoatl_path/'examples/optspeckle_2464x2056px_spec5px_8bit_gblur1px.tiff'
dice_path = Path('~/src/dice/build/bin/dice')
dice_path = Path('/home/rspencer/projects/DICe/build/bin/dice')
#%%
dice_opts= DiceOpts(input_file_name,
                    mod_file_name,
                    deformed_images,
                    subset_file,
                    output_folder,
                    dice_path)
dm = DiceManager(dice_opts)

#tf= DiceFilter(base_image,id_opts,camera,dice_opts,[50,150,200])
tf= DiceFilter(base_image,id_opts,camera,dice_opts,[2,4,5])


# Define an objective function
def displacement_match(data,endtime,external_data):
    # Want to get the displacement at final timestep to be close to 0.0446297
    # Using simdata for now.
    #disp_y = data.node_vars['disp_y']
    disp_y = data.data_fields['displacement'].data[:,1,-1]
    #print(np.abs(np.max(disp_y)-0.0446297))
    
    return np.abs(np.max(disp_y)-0.0446297)

# Instance cost function
c = CostFunction([displacement_match],None)

# Assign bounds
bounds  = {'neckWidth' : [0.5,1.]}

opt_inputs = OptimisationInputs(bounds,algorithm,None)

# Create run
mor = MooseOptimisationRun('ex4_Dice_Filter',opt_inputs,herd,c,data_filter=tf)

# Do 1 run.
mor.run(1)

S = mor._algorithm.result().F 
X = mor._algorithm.result().X
print('Target Elastic Modulus = 1E9')
print('Optimal Elastic Modulus = {}'.format(X[0]))
print('Absolute Difference = {}'.format(X[0]-1E9))
print('% Difference = {}'.format(100*(X[0]-1E9)/X[0]))
print('The optimisation run is backed up to:')
print('{}'.format(mor.get_backup_path()))
print('This can be restored using MooseOptimisationRun.restore_backup().')