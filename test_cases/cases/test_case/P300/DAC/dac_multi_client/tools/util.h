/******************************************************************************

                ��Ȩ���� (C), 1995-2014, �����Ϣ��ҵ�ɷ����޹�˾

 ******************************************************************************
  �� �� ��   : util.h
  ģ �� ��   :
  �� �� ��   :
  ��    ��   : ��� <wuhao@sugon.com>
  ��������   : 2016��8��26��
  ��������   : util.c��ͷ�ļ�

  �޸���ʷ   :
  1.��    ��   : 2016��8��26��
    ��    ��   : ��� <wuhao@sugon.com>
    �޸�����   : �����ļ�

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

