/******************************************************************************

                版权所有 (C), 1995-2014, 曙光信息产业股份有限公司

 ******************************************************************************
  文 件 名   : util.h
  模 块 名   :
  版 本 号   :
  作    者   : 吴昊 <wuhao@sugon.com>
  生成日期   : 2016年8月26日
  功能描述   : util.c的头文件

  修改历史   :
  1.日    期   : 2016年8月26日
    作    者   : 吴昊 <wuhao@sugon.com>
    修改内容   : 创建文件

******************************************************************************/
#ifndef __UTIL_H__
#define __UTIL_H__

#ifdef __cplusplus
    extern "C"{
#endif /* __cplusplus */

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

extern int setparam(int argc,char * argv [ ],mode_t * mode, mode_t dumask);


#ifdef __cplusplus
    }
#endif /* __cplusplus */

#endif /* __UTIL_H__ */

