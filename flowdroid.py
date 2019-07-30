#!/usr/bin/python

import subprocess, sys
import re
import os
from utilities import copyToFile

# TODO: change directory
androidJar = '/Users/angeli/Library/Android/sdk/platforms'

def run_flowdroid(apkPath):

    #TODO: check --TIMEOUT
    # run mudflow's version of flowdroid (added layoutmode none and fixed nopath to nopaths to their script)
    config = ['--logsourcesandsinks', '--pathalgo', 'sourcesonly', '--nopaths', '--aliasflowins', '--nostatic',
              '--aplength', '3', '--layoutmode', 'none', '--timeout', '43200']
    cmd = ['java', '-Xmx300g', '-jar', 'flowdroid.jar',  apkPath, androidJar] + list(config)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.flush()

    numLeak = 0
    # log output
    with open('data/log/' + os.path.splitext(os.path.basename(apkPath))[0] + '.txt', 'w') as f:
        for string in iter(p.stdout.readline, b''):
            sys.stdout.flush()
            line = string.decode('UTF-8').rstrip()
            f.write(line + '\n')
            f.flush()

            # print and return results
            if 'Exception in thread ' in line:
                print('exception')
