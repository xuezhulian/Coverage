import glob
import os
import sys
import shutil
import re
import string
from gitdiffmodel import PushDiff,CommitDiff,ClassDiff
from lcovinfomodel import LcovInfo,LcovClassInfo
import GitAnalyze
from GenerateEnv import GenerateEnv
import InfoAnalyze

pushdiff = PushDiff()
lcovinfo = LcovInfo()

def generateEnv():
  GenerateEnv()

  global OBJECT_FILE_DIR_normal
  global OBJECT_FILE_DIR_main
  global SRCROOT
  global SCRIPT_DIR
  global lcov
  global GCNO_DIR
  global GCDA_DIR

  OBJECT_FILE_DIR_normal        = os.environ['OBJECT_FILE_DIR_normal'].strip('\r')
  OBJECT_FILE_DIR_main          = os.environ['OBJECT_FILE_DIR_main'].strip('\r')
  SRCROOT                       = os.environ['SRCROOT'].strip('\r')
  SCRIPT_DIR                    = os.environ['SCRIPT_DIR']
  lcov                          = os.environ['lcov'].strip('\r')
  GCNO_DIR                      = os.environ['GCNO_DIR'].strip('\r')
  GCDA_DIR                      = os.environ['GCDA_DIR'].strip('\r')

def generateInfo():
  os.chdir(SCRIPT_DIR)

  changedfiles = map(lambda x:x.split('.')[0],pushdiff.changedClasses())
  if len(changedfiles) == 0:
    exit(0)

  sourcespath = SCRIPT_DIR + '/sources'
  if os.path.isdir(sourcespath):
    shutil.rmtree(sourcespath)
  os.makedirs(sourcespath)

  for filename in changedfiles:
    gcdafile = GCDA_DIR+'/'+filename+'.gcda'
    if os.path.exists(gcdafile):
      shutil.copy(gcdafile,sourcespath)
    else:
      print 'Error:GCDA file not found for %s' %gcdafile
      exit(1)
    gcnofile = GCNO_DIR + '/'+filename + '.gcno'
    if not os.path.exists(gcnofile):
      gcnofile = gcnofile.replace(OBJECT_FILE_DIR_normal,OBJECT_FILE_DIR_main)
      if not os.path.exists(gcnofile):
        print 'Error:GCNO file not found for %s' %gcnofile
        exit(1)
    shutil.copy(gcnofile,sourcespath)
  os.system(lcov + '-c -b %s -d %s -o \"Coverage.info\"' %(SCRIPT_DIR,sourcespath))
  if not os.path.exists(SCRIPT_DIR+'/Coverage.info'):
    print 'Error:failed to generate Coverage.info'
    exit(1)

  if os.path.getsize(SCRIPT_DIR+'/Coverage.info') == 0:
    print 'Error:Coveragte.info size is 0'
    os.remove(SCRIPT_DIR+'/Coverage.info')
    exit(1)

  shutil.rmtree(sourcespath)


def rewriteCommitMsg(pushdiff,lcovinfo):
  os.chdir(SRCROOT)

  if pushdiff == None or lcovinfo == None:
    return

  for classinfo in lcovinfo.classinfos:
    pushdiff.addhitlinesForClass(classinfo)

  print 'RCoverageRate:%.2f'%pushdiff.coveragerate()
  os.system('GIT_SEQUENCE_EDITOR=\"sed -i -re \'s/^pick /e /\'\" git rebase -i --autostash HEAD~%s'%len(pushdiff.commitdiffs))
  for i in reversed(range(0,len(pushdiff.commitdiffs))):
    commitdiff = pushdiff.commitdiffs[i]
    if not commitdiff:
      os.system('git rebase --abort')
      continue

    coveragerate = commitdiff.coveragerate()
    lines = os.popen('git log -1 --pretty=%B').readlines()

    commitMsg = lines[0].strip()
    commitMsgRe = re.compile('coverage: ([0-9\.-]*)')
    result = commitMsgRe.findall(commitMsg)
    if result:
      if result[0].strip() == '%.2f'%coveragerate:
        os.system('git rebase --continue')
        continue
      commitMsg = commitMsg.replace('coverage: %s'%result[0],'coverage: %.2f'%coveragerate)
    else:
      commitMsg = commitMsg + ' coverage: %.2f%%'%coveragerate
    lines[0] = commitMsg+'\n'
  
    stashName = 'commit-amend-stash'
    os.system('git stash save \'%s\';git commit --amend -m \'%s \' --no-edit;' %(stashName,''.join(lines)))
    if string.find(os.popen('cd %s;git stash list'%SRCROOT).readline(),stashName) != -1:
      os.system('git stash pop')
    
    os.system('git rebase --continue;')


if __name__ == "__main__":
  generateEnv()

  pushdiff = GitAnalyze.generatePushdiff()
  
  generateInfo()

  lcovinfo = InfoAnalyze.getLcovInfo(pushdiff) 
  
  rewriteCommitMsg(pushdiff,lcovinfo)
