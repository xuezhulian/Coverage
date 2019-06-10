#!/usr/bin/python

__author__ = "yuencong"
__date__ = "2019-03-20"
__license__ = "GPL"

import os
import sys
import re
import string

class GenerateEnv():
  def __init__(self):
    scriptdir()
    xcodeconfigdir()
    lcovtooldir()
    handlepoddir()
    gcnodir()
    gcdadir()

def scriptdir():
  global SCRIPT_DIR
  SCRIPT_DIR = sys.path[0]
  os.environ['SCRIPT_DIR'] = SCRIPT_DIR

def xcodeconfigdir():
  global OBJROOT
  global SRCROOT
  global OBJECT_FILE_DIR_normal
  global PRODUCT_BUNDLE_ID
  global TARGET_DEVICE_ID
  global BUILT_PRODUCTS_DIR

  envFilePath = SCRIPT_DIR+'/env.sh'
  if not os.path.exists(envFilePath):
    print 'Error:No env.sh,checkout whether exportenv.sh is config'
    exit(1)
  envFile = open(envFilePath,'r')
  envRe = re.compile('export (.*)=\"(.*)\"')
  for line in envFile.xreadlines():
    result = envRe.findall(line)
    if result:
      (envKey,envValue) = result[0]
      os.environ[envKey] = envValue
  envFile.close()

  OBJROOT                       = os.environ['OBJROOT'].strip('\r')
  SRCROOT                       = os.environ['SRCROOT'].strip('\r')
  OBJECT_FILE_DIR_normal        = os.environ['OBJECT_FILE_DIR_normal'].strip('\r')
  PRODUCT_BUNDLE_ID             = os.environ['PRODUCT_BUNDLE_IDENTIFIER'].strip('\r')
  TARGET_DEVICE_ID              = os.environ['TARGET_DEVICE_IDENTIFIER'].strip('\r')
  BUILT_PRODUCTS_DIR            = os.environ['BUILT_PRODUCTS_DIR'].strip('\r').split('/')[-1]
  #main repo object file,resolve the case when main and pod in same dir
  os.environ['OBJECT_FILE_DIR_main'] = OBJECT_FILE_DIR_normal
    
def lcovtooldir():
  lcov = SCRIPT_DIR + '/lcov/usr/bin/lcov '
  genhtml = SCRIPT_DIR + '/lcov/usr/bin/genhtml '
  os.environ['lcov'] = lcov
  os.environ['genhtml'] = genhtml

def handlepoddir():
  global OBJECT_FILE_DIR_normal
  global SRCROOT

  #default main repo  
  if len(sys.argv) != 2:
    return
  #filter coverage dir
  if sys.argv[1] == SCRIPT_DIR.split('/')[-1]:
    return
  repodir = sys.argv[1]
  SRCROOT = SCRIPT_DIR.replace(SCRIPT_DIR.split('/')[-1],repodir.strip())
  os.environ['SRCROOT'] = SRCROOT
  podspec = None
  for podspecPath in os.popen('find %s -name \"*.podspec\" -maxdepth 1' %SRCROOT).xreadlines():
    podspec = podspecPath.strip()
    break

  if podspec and os.path.exists(podspec):
    podspecFile = open(podspec,'r')
    snameRe = re.compile('s.name\s*=\s*[\"|\']([\w-]*)[\"|\']')
    for line in podspecFile.xreadlines():
      snameResult = snameRe.findall(line)
      if snameResult:
        break

    sname = snameResult[0].strip()
    OBJECT_FILE_DIR_normal = OBJROOT + '/Pods.build/%s/%s.build/Objects-normal'%(BUILT_PRODUCTS_DIR,sname)
    if not os.path.exists(OBJECT_FILE_DIR_normal):
      print 'Error:\nOBJECT_FILE_DIR_normal:%s  invalid path'%OBJECT_FILE_DIR_normal
      exit(1)
    os.environ['OBJECT_FILE_DIR_normal'] = OBJECT_FILE_DIR_normal

def gcnodir():
  GCNO_DIR = OBJECT_FILE_DIR_normal + '/x86_64'
  os.environ['GCNO_DIR'] = GCNO_DIR
  print("GCNO_DIR               :"+GCNO_DIR)

def gcdadir():
  GCDA_DIR = None
  USER_ROOT = os.environ['HOME'].strip()
  APPLICATIONS_DIR = '%s/Library/Developer/CoreSimulator/Devices/%s/data/Containers/Data/Application/' %(USER_ROOT,TARGET_DEVICE_ID)
  if not os.path.exists(APPLICATIONS_DIR):
    print 'Error:\nAPPLICATIONS_DIR:%s invaild file path'%APPLICATIONS_DIR
    exit(1)
  APPLICATION_ID_RE = re.compile('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
  for file in os.listdir(APPLICATIONS_DIR):
    if not APPLICATION_ID_RE.findall(file):
      continue
    plistPath = APPLICATIONS_DIR + file.strip() + '/.com.apple.mobile_container_manager.metadata.plist'
    if not os.path.exists(plistPath):
      continue
    plistFile = open(plistPath,'r')
    plistContent = plistFile.read()
    plistFile.close()
    if string.find(plistContent,PRODUCT_BUNDLE_ID) != -1:
      GCDA_DIR = APPLICATIONS_DIR + file + '/Documents/gcda_files'
      break
  if not GCDA_DIR:
    print 'GCDA DIR invalid,please check xcode config'
    exit(1)
  if not os.path.exists(GCDA_DIR):
    print 'GCDA_DIR:%s  path invalid'%GCDA_DIR
    exit(1)
  os.environ['GCDA_DIR'] = GCDA_DIR
  print("GCDA_DIR               :"+GCDA_DIR)
