#!/usr/bin/python

__author__ = "yuencong"
__date__ = "2019-03-20"
__license__ = "GPL"

from lcovinfomodel import LcovClassInfo

class PushDiff:
  def __init__(self):
    self.commitdiffs = []
    
  def contains_commitdiff(self,commitid):
    for commitdiff in self.commitdiffs:
      if commitdiff.commitid == commitid:
        return True
    return False

  def commitdiff(self,commitid):
    for commitdiff in self.commitdiffs:
      if commitdiff.commitid == commitid:
        return commitdiff
    return None

  def changedClasses(self):
    classes = set()
    for commitid in self.commitdiffs:
      for classdiff in commitid.classdiffs:
        if len(classdiff.changedlines) == 0:
          continue
        classname = classdiff.classname
        if classname.endswith('.m') or classname.endswith('.mm') or classname.endswith('.c'):
          classes.add(classname)
    
    return classes

  def changedLinesForClass(self,classname):
    changedlines = set()
    for commitdiff in self.commitdiffs:
      if commitdiff.contains_classdiff(classname):
        classdiff = commitdiff.classdiff(classname)
        changedlines = changedlines | classdiff.changedlines
    return changedlines

  def addhitlinesForClass(self,classinfo):
    for commitdiff in self.commitdiffs:
      if commitdiff.contains_classdiff(classinfo.classname):
        classdiff = commitdiff.classdiff(classinfo.classname)
        classdiff.hitlines = classinfo.hitlines & classdiff.changedlines
        classdiff.nohitlines = classinfo.nohitlines & classdiff.changedlines

  def coveragerate(self):
    hitlines = 0
    nohitlines = 0
    for commitdiff in self.commitdiffs:
      for classdiff in commitdiff.classdiffs:
        hitlines = hitlines + len(classdiff.hitlines)
        nohitlines = nohitlines + len(classdiff.nohitlines)
    if hitlines + nohitlines == 0:
      return -1

    return (hitlines / float(hitlines + nohitlines) * 100)


  def description(self):
    print '---------- PUSH DIFF DESCRIPTION'
    for commitdiff in self.commitdiffs:
      commitdiff.description()



class CommitDiff:
  def __init__(self,commitid):
    self.commitid = commitid
    self.classdiffs = set()

  def contains_classdiff(self,classname):
    for classdiff in self.classdiffs:
      if classdiff.classname == classname:
        return True
    return False

  def classdiff(self,classname):
    for classdiff in self.classdiffs:
      if classdiff.classname == classname:
        return classdiff

    classdiff = ClassDiff(classname)
    self.classdiffs.add(classdiff)
    return classdiff

  def coveragerate(self):
    hitlines = 0
    nohitlines = 0
    for classdiff in self.classdiffs:
      hitlines = hitlines + len(classdiff.hitlines)
      nohitlines = nohitlines + len(classdiff.nohitlines)
    
    if hitlines + nohitlines == 0:
      return -1
    return (hitlines/float(hitlines + nohitlines) * 100)
    
  def description(self):
    print '---------- COMMIT ID: %s' %self.commitid
    for classdiff in self.classdiffs:
      classdiff.description()
    


class ClassDiff:
  def __init__(self,classname):
    self.classname = classname
    self.changedlines = set()
    self.hitlines = set()
    self.nohitlines = set()

  def description(self):
    print '---------- CLASS NAME: %s' %self.classname
    print '---------- LINES: %s' %self.changedlines
    print '---------- HIT LINES: %s' %self.hitlines
    print '---------- NO HIT LINES: %s' %self.nohitlines