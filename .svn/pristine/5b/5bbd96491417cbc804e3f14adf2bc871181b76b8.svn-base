################################################################################
#                                                                              #
#        Copyright (C), 1995-2016, Sugon Information Industry Co., Ltd.        #
#                                                                              #
################################################################################
# File Name     : Makefile                                                     #
# Module Name   : test tools                                                   #
# Author        : wuhao <wuhao@sugon.com>                                      #
# Created Date  : 2016/10/10                                                   #
# Description   :                                                              #
#                                                                              #
# History       :                                                              #
# 1.Date         : 2016/10/10                                                  #
#   Author       : wuhao <wuhao@sugon.com>                                     #
#   Modification : Creating file                                               #
#                                                                              #
################################################################################
TOUCH:=touch
MKDIR:=mkdir
UCC :=gcc
# Include files

# Flags for all
UFLAGS := 

# Suppress display on screen
QUIET_UCC = @echo ' '  CC [U] '' $@;

# Macros
COMMON_OBJS := util.o 
TOUCH_OBJS := touch.o
MKDIR_OBJS := mkdir.o

.PHONY: all
all: $(TOUCH) $(MKDIR)

$(TOUCH): $(COMMON_OBJS) $(TOUCH_OBJS)
	$(QUIET_UCC)$(UCC) $(UFLAGS) -o $@ $^

$(MKDIR): $(COMMON_OBJS) $(MKDIR_OBJS)
	$(QUIET_UCC)$(UCC) $(UFLAGS) -o $@ $^

$(COMMON_OBJS): %.o:%.c
	$(QUIET_UCC)$(UCC) $(UFLAGS) -o $@ -c $<

$(TOUCH_OBJS): %.o:%.c
	$(QUIET_UCC)$(UCC) $(UFLAGS) -o $@ -c $<

$(MKDIR_OBJS): %.o:%.c
	$(QUIET_UCC)$(UCC) $(UFLAGS) -o $@ -c $<

dist:

clean:
	@rm -rf *.o $(TOUCH) $(MKDIR)
