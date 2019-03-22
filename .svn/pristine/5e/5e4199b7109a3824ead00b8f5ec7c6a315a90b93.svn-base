# -*-coding:utf-8 -*
import pandas as pd
import os
import sys
from pyecharts import Line, Overlap


def data_chart(file_name):
    print "Now processing data"
    d_path = os.path.dirname(__file__)
    logfile_format = os.path.join(d_path, "log.txt")
    if os.path.exists(logfile_format):
        os.remove(logfile_format)
    with open(file_name, "r") as fh:
        with open(logfile_format, "a+") as f:
            while True:
                line = fh.readline()
                line_lst = line.split()
                if len(line_lst) == 89 and line_lst[3].isdigit():
                    f.write("%s\t%s\t%s\t%s\t%s\n" % (line_lst[1], line_lst[14], line_lst[15], line_lst[16], line_lst[22]))
                if not line:
                    break

    reader = pd.read_table(logfile_format,
                           sep='\t',
                           engine='python',
                           names=["timestamp", "MB_read", "MB_write", "Read_rate", "Write_rate"],
                           header=None,
                           iterator=True)

    loop = True
    chunksize = 10000000
    chunks = []
    while loop:
        try:
            chunk = reader.get_chunk(chunksize)
            chunks.append(chunk)
        except StopIteration:
            loop = False
            print "Data process finish, now generating the chart"

    df = pd.concat(chunks)

    overlap = Overlap()
    line = Line("性能曲线图")
    line1 = Line()
    line.width = 1280
    line1.width = 1280
    x = df["timestamp"]
    y1 = df["MB_read"]
    y2 = df["MB_write"]
    y3 = df["Read_rate"]
    y4 = df["Write_rate"]
    line.add("读带宽", x, y1,
             is_datazoom_show=True,
             tooltip_trigger='axis',
             is_more_utils=True,
             is_stack=True,
             yaxis_formatter=" MB")
    line.add("写带宽", x, y2,
             is_datazoom_show=True,
             tooltip_trigger='axis',
             is_more_utils=True,
             is_stack=True,
             yaxis_formatter=" MB")
    line1.add("读IOPS", x, y3,
              is_datazoom_show=True,
              tooltip_trigger='axis',
              is_more_utils=True,
              is_stack=True)
    line1.add("写IOPS", x, y4,
              is_datazoom_show=True,
              tooltip_trigger='axis',
              is_more_utils=True,
              is_stack=True)

    overlap.add(line)
    overlap.width = 1280
    overlap.add(line1,
                yaxis_index=1,
                is_add_yaxis=True)
    overlap.render()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Please input the path of vdbench output: python analysis_iops \033[1;31;40m/your/vdbench/output/path\033[0m"
        sys.exit(1)
    f_path = sys.argv[1]
    f_name = "%s/flatfile.html" % f_path
    data_chart(f_name)
