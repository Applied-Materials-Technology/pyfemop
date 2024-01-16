#
#
# Import all necessary packages

import numpy as np
from matplotlib import pyplot as plt
from pyfemop.optimisationmanager.optimisationmanager import MooseOptimisationRun


print('------------------------------------------------')
print('                  Example-3                     ')
print('              Run Visualisation           ')
print('------------------------------------------------')

# Import example 1 run
mor = MooseOptimisationRun.restore_backup('examples/ex2_simple_geometry.pickle')

# Get algorithm history



