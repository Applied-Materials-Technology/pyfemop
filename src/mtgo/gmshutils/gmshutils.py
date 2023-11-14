#
# Code to update .geo file parameters
# ToDo

import os

def RunGmsh(gmsh_path,input_file):
    """Run the .geo file given

    Args:
        input_file (string): Path to the .geo file containing the input.
    """

    if os.path.splitext(input_file)[1] != '.geo':
        raise FileNotFoundError('Incorrect file type. Must be .geo.')
    
    if not os.path.exists(input_file):
        raise FileNotFoundError('File not found.')
    
    call_string = '{} {}'.format(gmsh_path,input_file)
    os.system(call_string)