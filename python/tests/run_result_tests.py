
# import runpy 

#runpy.run_path(path_name='tests/bathclamp_vclamp_cal.py')

exec(open('tests/bathclamp_vclamp_cal.py').read())
exec(open('tests/bathclamp_vclamp_step_response.py').read())

#from bathclamp_vclamp_cal import *
#from bathclamp_vclamp_step_response import *

print('Tests done. Check python/results folder')