/******************************************************************************

                版权所有 (C), 1995-2014, 曙光信息产业股份有限公司

 ******************************************************************************
  文 件 名   : touch.c
  模 块 名   :
  版 本 号   :
  作    者   : 吴昊 <wuhao@sugon.com>
  生成日期   : 2016年8月24日
  功能描述   : 测试dac工具函数集合

  修改历史   :
  1.日    期   : 2016年8月24日
    作    者   : 吴昊 <wuhao@sugon.com>
    修改内容   : 创建文件

******************************************************************************/
#include "util.h"

int main(int argc, char * argv[])
{
    int ret = 0;
    int fd = -1;
    mode_t mode = 0;
    mode_t dumask = 0666;
    char * filename = NULL;

    ret = setparam(argc, argv, &mode, dumask);
    if (ret < 0)
    {
        printf("Invalid arguments\n");
        goto l_end;
    }

    filename = argv[1];

    fd = creat(filename, mode);
    if (fd == -1)
    {
        ret = -errno;
        printf("touch: can not create file '%s' mode '%o': %d\n",
                            filename, mode, ret);
        goto l_end;
    }

    close(fd);

l_end:
    return ret;
}

