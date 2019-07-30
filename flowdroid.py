#!/usr/bin/python

import subprocess, sys
import re
import os
from utilities import copy_to_file

# TODO: change directory
androidJar = '/Users/angeli/Library/Android/sdk/platforms'


def run_flowdroid(apkPath):

    #TODO: check --TIMEOUT , '--layoutmode', 'none', '--timeout', '43200'
    # run mudflow's version of flowdroid (added layoutmode none and fixed nopath to nopaths to their script)
    config = ['--logsourcesandsinks', '--pathalgo', 'sourcesonly', '--nopaths', '--aliasflowins', '--nostatic',
              '--aplength', '3', '--layoutmode', 'none', '--timeout', '43200']
    cmd = ['java', '-Xmx300g', '-jar', 'flowdroid.jar',  apkPath, androidJar] + list(config)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.flush()

    # log output
    apk_name = os.path.splitext(os.path.basename(apkPath))[0]
    with open('data/log/' + apk_name + '.txt', 'w') as f:
        for string in iter(p.stdout.readline, b''):
            sys.stdout.flush()
            line = string.decode('UTF-8').rstrip()
            f.write(line + '\n')
            f.flush()
