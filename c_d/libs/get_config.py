#!/usr/bin/python
# -*-coding:utf-8 -*
import ConfigParser

import log

config = ConfigParser.ConfigParser()
config.read('/home/StorTest/c_d/conf')
sections = config.sections()
# log.debug(sections)
# if config.has_option(sections[0], 'filenums'):
#     default_filenums = config.get(sections[0], 'filenums')
#     print default_filenums
#     # log.debug(default_filenums)
# if config.has_option(sections[0], 'width'):
#     default_width = config.get(sections[0], 'width')