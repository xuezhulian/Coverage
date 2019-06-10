#!/usr/bin/env python
#coding=utf-8

import os
import stat
import sys
import string

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


def gen_by_componet_name(name):
    content = """
cd ../RCodeCoverage
echo '----------------'
rate=$(python coverage.py %s | grep "RCoverageRate:" | sed 's/RCoverageRate:\([0-9-]*\).*/\\1/g')
if [ $rate -eq -1 ]; then
	echo '没有覆盖率信息，跳过...'
	exit 0
fi

if [ $(echo "$rate < 80.0" | bc) = 1 ];then
		echo '代码覆盖率为'$rate'，不满足需求'
		echo '----------------'
    exit 1
else
		echo '代码覆盖率为'$rate'，即将上传代码'
fi
echo '----------------'
exit 0
""" % (name,)
    return content


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
        if os.path.isdir(dirpath + '/' + file):
            dirlists.add(file)

    for name in dirlists:
        dirpath = sys.path[0]
        dirpath = dirpath.replace(dirpath.split('/')[-1],name)
        filepath = os.path.join(dirpath, '.git', 'hooks', 'pre-push.sample')
        if os.path.exists(filepath):
            os.rename(filepath,filepath[0:-7])
        filepath = filepath[0:-7]

        if not os.path.exists(filepath):
            continue
        with open(filepath, 'wb') as f:
            if name == 'RBigApp':
                name = ''
            f.write(gen_by_componet_name(name).encode(encoding='UTF-8'))
        os.chmod(filepath, stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)
