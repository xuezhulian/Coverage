#!/usr/bin/env python
#coding=utf-8

import os
import sys

if __name__ == '__main__':
    dirpath = sys.path[0]
    dirpath = '/'.join(dirpath.split('/')[0:-1])
    if not os.path.exists(dirpath):
        print 'pre push hook failed with invalid dirpath'
        exit()

    dirlists = set()
    for file in os.listdir(dirpath):
        if file == 'RCodeCoverage':
            continue
        if os.path.exists(dirpath + '/' + file + '/.git/hooks/pre-push'):
            dirlists.add(dirpath + '/' + file + '/.git/hooks/pre-push')

    for name in dirlists:
        os.remove(name)
    print u'已移除代码覆盖率检查'
