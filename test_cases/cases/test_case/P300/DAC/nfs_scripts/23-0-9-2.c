#include<stdio.h>
#include<stdlib.h>
#include<sys/types.h>
#include<unistd.h>
void main()
{
 gid_t gid;
 gid = getegid();
 printf("%d",gid);
}
