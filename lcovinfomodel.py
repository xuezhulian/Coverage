#!/usr/bin/python

__author__ = "yuencong"
__date__ = "2019-03-20"
__license__ = "GPL"

class LcovInfo:
  def __init__(self):
    self.classinfos = set()

  def lcovclassinfo(self,classname):
    for classinfo in self.classinfos:
      if classinfo.classname == classname:
        return classinfo
    classinfo = LcovClassInfo(classname)
    self.classinfos.add(classinfo)
    return classinfo
    
  def description(self):
    print '---------- LCOV INFO'
    for classinfo in self.classinfos:
      classinfo.description()

class LcovClassInfo:
  def __init__(self,classname):
    self.classname = classname
    self.hitlines = set()
    self.nohitlines = set()
  def description(self):
    print '---------- LCOV CLASS NAME:%s'%self.classname
    print '---------- LCOV CLASS HIT LINES:%s'%self.hitlines
    print '---------- LCOV CLASS NO HIT LINES:%s'%self.nohitlines

