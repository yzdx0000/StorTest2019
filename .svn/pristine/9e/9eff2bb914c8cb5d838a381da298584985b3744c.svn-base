/******************************************************************************

                版权所有 (C), 1995-2014, 曙光信息产业股份有限公司

 ******************************************************************************
  文 件 名   : util.c
  模 块 名   : tools
  版 本 号   :
  作    者   : 吴昊 <wuhao@sugon.com>
  生成日期   : 2016年8月26日
  功能描述   : 工具通用函数

  修改历史   :
  1.日    期   : 2016年8月26日
    作    者   : 吴昊 <wuhao@sugon.com>
    修改内容   : 创建文件

******************************************************************************/

#include "util.h"

int setparam(int argc, char * argv[], mode_t * mode, mode_t dumaks)
{
    char * modestr  = NULL;
    mode_t sysumask = 0;
    int ret = 0;

    if (argc <= 1 || argc > 3)
    {
        printf("Invalid argument\n");
        ret = -EINVAL;
        goto l_end;
    }

    modestr  = argv[2];

    sysumask = umask(0);

    if (NULL == modestr)
    {
        *mode = dumaks & ~sysumask;
    }
    else
    {
        *mode = strtoul(modestr, NULL, 8);
    }

l_end:
    return ret;
}


