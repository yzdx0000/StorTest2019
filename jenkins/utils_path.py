import os
import sys

# /StorTest/jenkins
current_path = os.path.dirname(os.path.abspath(__file__))
# /StorTest/
stortest_case_path = os.path.dirname(current_path)
sys.path.append(os.path.join(stortest_case_path, 'test_cases', 'libs'))