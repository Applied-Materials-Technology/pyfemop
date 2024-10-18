#%%

import yaml
import numpy as np
#from pathlib import Path

#%%

run_config = {
    "moose_config" : {
        'main_path': '/home/rspencer/projects/moose',
        'app_path': '/home/rspencer/projects/sloth',
        'app_name': 'sloth-opt'
    },
    "gmsh_path" : '/home/rspencer/src/gmsh/bin/gmsh',
    "external_data": '/home/rspencer/moose_work/Geometry_Optimisation/mat_opt/baseline_mat.e',
    "run_dir": '/home/rspencer/moose_work/Geometry_Optimisation/mat_opt/Run',
    "moose_input": '/home/rspencer/moose_work/Geometry_Optimisation/mat_opt/creep_x_plane_circ_sinh_3d_dmg_nl.i',
    "gmsh_input" : '/home/rspencer/moose_work/Geometry_Optimisation/mat_opt/x_plane_circ.geo',
    "run_name" : 'XC_Mat_1',
    "n_generations" :1,
    "n_para" : 2,
    "n_dirs" : 2,
    "bounds" :  {
        'alpha': [1.68E-9,2.06E-9],
        'beta': [0.018,0.022],
        'dam_a': [465.3,568.7],
        'dam_phi': [2.25,2.75],
        'dam_zeta': [11.25,13.75],
           }
}


# %%
with open("/home/rspencer/pyfemop/examples/yaml_test.yaml", mode="wt", encoding="utf-8") as file:
    yaml.dump(run_config, file)
# %%
with open("/home/rspencer/pyfemop/examples/yaml_test.yaml", mode="rt", encoding="utf-8") as file:
    test = yaml.safe_load(file)
# %%
print(test)
# %%
test['external_data']


# %%
