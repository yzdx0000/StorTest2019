/******************************************************************************

                ��Ȩ���� (C), 1995-2014, �����Ϣ��ҵ�ɷ����޹�˾

 ******************************************************************************
  �� �� ��   : mkdir.c
  ģ �� ��   :
  �� �� ��   :
  ��    ��   : ��� <wuhao@sugon.com>
  ��������   : 2016��8��26��
  ��������   : mkdir����ʵ��

  �޸���ʷ   :
  1.��    ��   : 2016��8��26��
    ��    ��   : ��� <wuhao@sugon.com>
    �޸�����   : �����ļ�

******************************************************************************/
#include "util.h"

int main(int argc, char * argv[])
{
    int ret = 0;
    int fd = -1;
    mode_t mode = 0;
    mode_t dumask = 0777;
    char * filename = NULL;


    ret = setparam(argc, argv, &mode, dumask);
    if (ret < 0)
    {
        printf("Invalid arguments\n");
        goto l_end;
    }

    filename = argv[1];

    fd = mkdir(filename, mode);
    if (fd == -1)
    {
        ret = -errno;
        printf("mkdir: can not creat directory '%s' mode '%o': %d\n",
                                  filename, mode, ret);
        goto l_end;
    }

    close(fd);

l_end:
    return ret;
}

