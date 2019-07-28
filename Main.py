import multiprocessing as mp
import glob
import shutil
import uuid
import pandas as pd
from Excel_Helper import append_df_to_excel

apksPath = '/Users/angeli/My_Documents/Mudflow/apks'
filesPath = 'data/'
fileWithColumnNames = '/Users/angeli/PycharmProjects/mudflow/data/Column_Names.xlsx'
count = 0
filePath = ''


def create_new_file():
    global filePath
    uniqueFileName = str(uuid.uuid4().hex)
    filePath = filesPath + uniqueFileName + '.xlsx'
    shutil.copy(fileWithColumnNames, filePath)


def processApk(apk):
    global count
    global filePath
    print(apk + ' ' + str(count))
    if count == 0:
        create_new_file()
    if count > 1:
        count = 0
        create_new_file()
    df = pd.DataFrame([1,2,3,4,5]).T
    append_df_to_excel(filePath, df, header=None)
    count = count + 1

def create_mudflow_file(apks_csv_path):
    //