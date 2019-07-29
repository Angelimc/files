import shutil

from pandas import DataFrame
import concurrent.futures

from ExcelHelper import append_df_to_excel
from SourcesSinks import appendToFile, copyToFile
from Flowdroid import runFlowdroid
from Flowdroid20 import runFlowdroid20
from Flowdroid import runflowdroid
import glob
import pandas as pd
import re

excelPath = 'data/Test_Data.xlsx'
fileWithColumns = 'data/Column_Names.xlsx'
apksPath = 'apks'
sourceSinkPath = 'SourcesAndSinks.txt'


def addSource(str):
    p = re.compile(r'.+\)$')
    if re.search(p, str):
        str = '<' + str + '> -> _SOURCE_'
        with open(sourceSinkPath, 'w') as f:
            f.write(str + '\n')
    else:
        p2 = re.compile('NO_SENSITIVE_SOURCE')
        if re.search(p2, str):
            copyToFile('sourceSinkFiles/NO_SENSITIVE_SOURCE.txt', sourceSinkPath)
        else:
            with open(sourceSinkPath, 'w') as f:
                f.write('')


def addSink(str):
    p = re.compile(r'.+\)$')
    if re.search(p, str):
        str = '<' + str + '> -> _SINK_'
        with open(sourceSinkPath, 'a+') as f:
            f.write(str)
    else:
        p2 = re.compile('NO_SENSITIVE_SINK')
        if re.search(p2, str):
            appendToFile('sourceSinkFiles/NO_SENSITIVE_SINK.txt', sourceSinkPath)


def createMudflowFile():
    #shutil.copy(fileWithColumns, excelPath)
    cols = pd.read_excel(excelPath, sheet_name='Sheet1').columns
    for apk in glob.glob(apksPath + '/*.apk'):
        data = []
        print(apk)
        # add apk name to row
        for i in range(len(cols)):
            if i == 0:
                continue
            if cols[i] == 'name':
                data.append(apk)
                continue
            # extract source and sink
            result = [x.strip() for x in cols[i].split('->')]
            if result and len(result) == 2:
                addSource(result[0])
                addSink(result[1])
                # add number of leaks to row
                numLeaks = runFlowdroid(apk, sourceSinkPath, None, result[0] + result[1])
                data.append(numLeaks)
                print(cols[i] + ': ' + str(numLeaks))
            else:
                print('wrong format: ' + cols[i])
                data.append('')
        df = DataFrame(data).T
        append_df_to_excel(excelPath, df, header=None)
        print('appended row to file')


#createMudflowFile()