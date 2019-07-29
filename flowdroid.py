#!/usr/bin/python

import subprocess, sys
import re
import os
from Utilities import copyToFile

# TODO: change directory
androidJar = '/Users/angeli/Library/Android/sdk/platforms'

def run_flowdroid(apkPath):
    print(apkPath)

    #TODO: add --TIMEOUT
    # run mudflow's version of flowdroid (added layoutmode none to their script)
    config = ['--logsourcesandsinks', '--pathalgo', 'sourcesonly', '--nopaths', '--aliasflowins', '--nostatic',
              '--aplength', '3', '--layoutmode', 'none']
    cmd = ['java', '-Xmx300g', '-jar', 'flowdroid.jar',  apkPath, androidJar] + list(config)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.flush()

    numLeak = 0
    # log output
    with open('data/log/' + os.path.splitext(os.path.basename(apkPath))[0] + '.txt', 'w') as f:
        for string in iter(p.stdout.readline, b''):
            sys.stdout.flush()
            line = string.decode('utf-8').rstrip()
            f.write(line + '\n')

            # print and return results
            if 'No sources found' in line:
                return
            if 'No sinks found' in line:
                return
            if 'No sources or sinks found' in line:
                return
            if 'exception ' in line.lower():
                print('exception')
            if 'No results found' in line:
                return
            if ' - - ' in line:
                numLeak = numLeak + 1

    if numLeak:
        return int(numLeak)
    print('check for errors: ' + os.path.basename(apkPath))