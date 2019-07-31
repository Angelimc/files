#!/usr/bin/python

import os
import subprocess
import sys

#TODO: change back to /data/Junbin/android-platforms
androidJar = '/Users/angeli/Library/Android/sdk/platforms'

#TODO 'timeout', '12h',
def run_flowdroid(apkPath):
    # run mudflow's version of flowdroid (added layoutmode none and fixed nopath to nopaths to their script)
    config = ['--logsourcesandsinks', '--pathalgo', 'sourcesonly', '--nopaths', '--aliasflowins', '--nostatic',
              '--aplength', '3', '--layoutmode', 'none']
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
