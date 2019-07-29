#!/usr/bin/python

import subprocess, sys
import re
import os
from SourcesSinks import copyToFile

androidJar = '/Users/angeli/Library/Android/sdk/platforms'
flowdroidJar = 'flowdroidJars/flowdroid.jar'

def runFlowdroid(apkPath, sourcesSinks, customConfig, name):
    print(os.path.basename(apkPath))
    print(os.path.basename(sourcesSinks))
    # 'SourcesAndSinks.txt' must be in root directory for this version
    if sourcesSinks != 'SourcesAndSinks.txt':
        copyToFile(sourcesSinks, 'SourcesAndSinks.txt')

    # run mudflow's version of flowdroid (added layoutmode none to their script)
    config = ['--logsourcesandsinks', '--pathalgo', 'sourcesonly', '--nopaths', '--aliasflowins', '--nostatic',
              '--aplength', '3', '--layoutmode', 'none']
    if customConfig:
        config = config + customConfig
    cmd = ['java', '-Xmx300g', '-jar', flowdroidJar,  apkPath, androidJar] + list(config)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.flush()

    # log output
    with open('data/log/' + os.path.basename(apkPath) + '_' + name[-30:] + '.txt', 'w') as f1:
        f1.write(os.path.basename(sourcesSinks))
    with open('data/log/' + os.path.basename(apkPath) + '_' + name[-30:] + '.txt', 'a+') as f2:
        numLeak = 0
        for line in iter(p.stdout.readline, b''):
            sys.stdout.flush()
            str = line.decode('utf-8').rstrip()
            f2.write(str + '\n')

            # print and return results
            if 'No sources found' in str:
                print('no sources found')
                return 0
            if 'No sinks found' in str:
                print('no sinks found')
                return 0
            if 'No sources or sinks found' in str:
                print('no sources or sinks found')
                return 0
            if 'No results found' in str:
                print('no results found')
                return 0
            if ' - - ' in str:
                numLeak = numLeak + 1

    if numLeak:
        return int(numLeak)
    return -1