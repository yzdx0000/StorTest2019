# -*- coding:utf-8 -*-
import os

def result(case_num, result_code):
    """
    | test case | case_num | result_code |
    | 测试结果记录 | 12345 | 0 |
    | | 用例序列号 |  测试结果标识 |
    """
    result_code = str(result_code)
    result_path = '/tmp/result'

    if os.path.exists(result_path):
        pass
    else:
        with open(result_path, 'w') as f:
            f.write('case' + '\t' + 'code' + '\n')
            f.flush()

    f1 = open(result_path, 'r+')
    lines = f1.readlines()

    for i in range(len(lines)):
        if lines[i][0].isdigit():
            if lines[i].split()[0] == case_num:
                lines_tmp = lines[i].replace(lines[i], '')
                lines[i] = lines_tmp
    f1 = open(result_path, 'w+')
    f1.writelines(lines)
    f1.flush()
    f1.close()

    with open(result_path, 'a') as f:
        f.write(case_num + '\t' + result_code + '\n')
        f.flush()
