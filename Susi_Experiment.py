#!/usr/bin/python

import glob

from flowdroid import runflowdroid
from flowdroid import run_flowdroid
from Flowdroid20 import runFlowdroid20
from pandas import DataFrame
from ExcelHelper import append_df_to_excel
import os

filename = 'data/Susi_Category.xlsx'
sourceSinkPath = 'sourceSinkFiles/both/'
#apksPath = '/Users/angeli/My_Documents/Mudflow/apks/testfile_susi'
apksPath = 'apks'
sourceCategories = ['HARDWARE_INFO', 'UNIQUE_IDENTIFIER', 'LOCATION_INFORMATION', 'NETWORK_INFORMATION', 'ACCOUNT_INFORMATION',
           'EMAIL', 'FILE_INFORMATION', 'BLUETOOTH_INFORMATION', 'VOIP', 'DATABASE_INFORMATION',
           'PHONE_INFORMATION', 'AUDIO', 'SMS_MMS', 'CONTACT_INFORMATION', 'CALENDAR_INFORMATION', 'SYSTEM_SETTINGS',
           'IMAGE', 'BROWSER_INFORMATION', 'NFC', 'NO_SENSITIVE_SOURCE', 'CONTENT_RESOLVER']
customConfig = ['--singleflow']

def createSusiFile():
    # overwrites existing file
    #if os.path.exists(filename):
    #    os.remove(filename)
    for apk in glob.glob(apksPath + '/*.apk'):
        print(apk + ': ')
        for category in sourceCategories:
            numLeaks = run_flowdroid(apk, sourceSinkPath + category + '.txt', None, os.path.basename(sourceSinkPath))
            if numLeaks > 0:
                df = DataFrame([os.path.basename(apk), category]).T
                append_df_to_excel(filename, df, header=None)
            print(numLeaks)

if __name__ =='__main__':
    createSusiFile()
