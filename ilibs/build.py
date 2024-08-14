import os
import shutil

os.system('python setup.py build_ext --inplace')
shutil.rmtree('build')