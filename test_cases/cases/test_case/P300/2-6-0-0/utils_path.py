import os
import sys

#/home/StorTest/test_cases/cases/test_case/P300/2-6-0-0
current_path = os.path.dirname(os.path.abspath(__file__))
#/home/StorTest/test_cases/cases/test_case/P300
P300_path = os.path.dirname(current_path)
# /StorTest/test_cases/cases/test_case
test_case_path = os.path.dirname(P300_path)
# /StorTest/test_cases/cases
cases_path = os.path.dirname(test_case_path)
# /StorTest/test_cases
test_cases = os.path.dirname(cases_path)
# /StorTest/test_cases/libs
libs_path = os.path.join(test_cases, 'libs')
sys.path.append(libs_path)
# /StorTest/test_cases/cases/test_case/P300/fault/fault_test/lib
fault_lib_path = os.path.join(P300_path, 'fault/fault_test/lib')
sys.path.append(fault_lib_path)


vdbench_log_path = os.path.join(test_cases, 'log', 'vdbench_log')

# /StorTest
StorTest = os.path.dirname(test_cases)
# /StorTest/scripts
scripts_path = os.path.join(StorTest, 'scripts')
sys.path.append(scripts_path)

