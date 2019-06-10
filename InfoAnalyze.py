#!/usr/bin/python

__author__ = "yuencong"
__date__ = "2019-03-21"
__license__ = "GPL"

import os
import sys
import re
import string
from lcovinfomodel import LcovInfo,LcovClassInfo
from gitdiffmodel import PushDiff,CommitDiff,ClassDiff

def getLcovInfo(pushdiff):
  SCRIPT_DIR                    = os.environ['SCRIPT_DIR']
  lcov                          = os.environ['lcov'].strip('\r')
  genhtml                       = os.environ['genhtml'].strip('\r')
  os.chdir(SCRIPT_DIR)
  lcovInfo = LcovInfo()

  if not os.path.exists('Coverage.info'):
    print 'Error:No Coverage.info'
    exit(1)

  if os.path.getsize('Coverage.info') == 0:
    print 'Error:Coveragte.info size is 0'
    os.remove('Coverage.info')
    exit(1)

  #filter the file not recorded in git 
  headerFileRe = re.compile("([0-9a-zA-Z\+]*\.[h|m|mm|c]+)")
  changedClasses = pushdiff.changedClasses()
  filterClasses = set()
  for line in os.popen(lcov + ' -l Coverage.info').xreadlines():
    result = headerFileRe.findall(line)
    if result and not result[0].strip() in changedClasses:
      filterClasses.add(result[0].strip())
  if len(filterClasses) != 0:
    os.system(lcov + '--remove Coverage.info *%s* -o Coverage.info' %'* *'.join(filterClasses))
  
  if os.path.getsize('Coverage.info') == 0:
    os.remove('Coverage.info')
    return
  #filter unused lines
  infoFiler = open('Coverage.info','r')
  lines = infoFiler.readlines()
  infoFiler.close()

  infoFilew = open('Coverage.info','w')
  # DA:<line number>,<execution count>[,<checksum>] 
  DARe = re.compile('^DA:([0-9]*),([0-9]*)')

  changedlines = None
  lcovclassinfo = None
  #generate lcov data model
  for line in lines:
    #match file name
    if line.startswith('SF:'):
      infoFilew.write('end_of_record\n')
      classname = line.strip().split('/')[-1].strip()
      changedlines = pushdiff.changedLinesForClass(classname)
      if len(changedlines) == 0:
        lcovclassinfo = None
      else:
        lcovclassinfo = lcovInfo.lcovclassinfo(classname)
        infoFilew.write(line)

    if not lcovclassinfo:
      continue
    #match lines
    DAResult = DARe.findall(line)
    if DAResult:
      (startIndex,count) = DAResult[0]
      if not int(startIndex) in changedlines:
        continue
      infoFilew.write(line)
      if int(count) == 0:
        lcovclassinfo.nohitlines.add(int(startIndex))
      else:
        lcovclassinfo.hitlines.add(int(startIndex))
      continue

  infoFilew.write('end_of_record\n')
  infoFilew.close() 

  #genhtml
  if not os.path.getsize('Coverage.info') == 0:
    os.system(genhtml + 'Coverage.info -o Coverage')
  os.remove('Coverage.info')

  return lcovInfo