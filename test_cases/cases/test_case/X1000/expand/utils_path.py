import os
import sys
current_path = os.path.dirname(os.path.abspath(__file__))
case_path = current_path.split('expand')[0]
print case_path
sys.path.append('/home/StorTest/test_cases/libs')
sys.path.append(case_path + 'lun_manager')