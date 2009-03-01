from __future__ import with_statement

import os
import shutil
import json

#This could have been done just as well with OO, but I saw no compelling benefit too it
#If it really bothers someone feel free to change it

from pymt.logger import pymt_logger

pymt_home_dir = os.path.expanduser('~/.pymt/')
colors_json_dir = os.path.join(pymt_home_dir, 'colors.json')

#If they don't have a colors file, give them one
if not os.path.exists(colors_json_dir):
    from distutils.sysconfig import get_python_lib
    original = os.path.join(get_python_lib(), 'pymt/data/colors.json')
    shutil.copy(original, pymt_home_dir)
    
    pymt_logger.info('No color configuration file found.  Creating one now in %s', pymt_home_dir + 'colors.json')

#Now get the colors out of the file and into a dictionary
with open(colors_json_dir, 'r') as json_file:
    color_dict = json.load(json_file)

#Generate local variables so you don't have to access the colors through a dict
for key, color in color_dict.items():
    #We cast them to tuples to force the user to use the change function to change them
    #This way we make sure the json file is updated whever a color changes
    exec(key + ' = tuple('  + str(color) +')')
def change(color, value):
    if type(value) is not tuple:
        print 'color.change takes a tuple, not %s', type(value)
        raise TypeError
    exec(color + ' = ' + str(value))
    color_dict[color] = value
    #Delete the json file
    os.remove(colors_json_dir)
    #Regenerate it
    json_file = open(colors_json_dir, 'wt')
    json.dump(color_dict, json_file)
