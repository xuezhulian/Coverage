#!/usr/bin/python

__author__ = "yuencong"
__date__ = "2019-03-21"
__license__ = "GPL"

import re
import os
import string
from gitdiffmodel import PushDiff,CommitDiff,ClassDiff
    
def generatePushdiff():
  SRCROOT                       = os.environ['SRCROOT'].strip()
  SCRIPT_DIR                    = os.environ['SCRIPT_DIR'].strip('\r')  
  os.chdir(SRCROOT)
  pushdiff = PushDiff()


  #TODO: MAYBE BETTER METHOD
  aheadCommitRe = re.compile('Your branch is ahead of \'.*\' by ([0-9]*) commit')
  aheadCommitNum = None
  for line in os.popen('git status').xreadlines():
    result = aheadCommitRe.findall(line)
    if result:
      aheadCommitNum = result[0]
      break
  
  if aheadCommitNum:
    for i in range(0,int(aheadCommitNum)):
      commitid = os.popen('git rev-parse HEAD~%s'%i).read().strip()
      pushdiff.commitdiffs.append(CommitDiff(commitid))
    stashName = 'git-diff-stash'
    os.system('git stash save \'%s\'; git log -%s -v -U0> "%s/diff"'%(stashName,aheadCommitNum,SCRIPT_DIR))
    if string.find(os.popen('git stash list').readline(),stashName) != -1:
      os.system('git stash pop')
  else:
    #prevent change last commit msg without new commit 
    print 'No new commit'
    exit(1)

  if not os.path.exists(SCRIPT_DIR + '/diff'):
    print 'No diff file'
    exit(1)

  diffFile = open(SCRIPT_DIR+'/diff')

  commitidRe = re.compile('commit (\w{40})')
  classRe = re.compile('\+\+\+ b(.*)')
  changedLineRe = re.compile('\+(\d+),*(\d*) \@\@')

  commitdiff = None
  classdiff = None

  for line in diffFile.xreadlines():
    #match commit id
    commmidResult = commitidRe.findall(line)
    if commmidResult:
      commitid = commmidResult[0].strip()
      if pushdiff.contains_commitdiff(commitid):
        commitdiff = pushdiff.commitdiff(commitid)
      else:
        #TODO filter merge
        commitdiff = None

    if not commitdiff:
      continue

    #match class name
    classResult = classRe.findall(line)
    if classResult:
      classname = classResult[0].strip().split('/')[-1]
      classdiff = commitdiff.classdiff(classname)

    if not classdiff:
      continue

    #match lines
    lineResult = changedLineRe.findall(line)
    if lineResult:
      (startIndex,lines) = lineResult[0] 
      # add nothing
      if cmp(lines,'0') == 0:
        pass        
      #add startIndex line
      elif cmp(lines,'') == 0:
        classdiff.changedlines.add(int(startIndex))
      #add lines from startindex
      else:
        for num in range(0,int(lines)):
          classdiff.changedlines.add(int(startIndex) + num)

  diffFile.close()
  os.remove(SCRIPT_DIR+'/diff')
  
  return pushdiff
