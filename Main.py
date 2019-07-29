import multiprocessing as mp
import glob
import os
import shutil
import uuid
import pandas as pd
from Excel_Helper import append_df_to_excel
import csv

process_num = None
mudflow_dir = 'data/mudflow/'
fileWithColumnNames = '/Users/angeli/PycharmProjects/mudflow/data/Column_Names.xlsx'
count = 0
filePath = ''


def create_new_file():
    global filePath
    unique_id = str(uuid.uuid4().hex)
    filePath = mudflow_dir + 'process_' + process_num + '/' + str(uuid.uuid4().hex) + '.xlsx'
    shutil.copy('data/Column_Names.xlsx', filePath)


def process_apk(apk):
    global count
    global filePath
    """
    print(apk + ' ' + str(count))
    if count == 0:
        create_new_file()
    if count >= 2: #change to 99 later
        count = 0
        create_new_file()
    df = pd.DataFrame([1,2,3,4,5]).T
    append_df_to_excel(filePath, df, header=None)
    count = count + 1
    """


def create_mudflow_file(apks_csv_path):
    global mudflow_dir
    process_num = os.path.splitext(apks_csv_path)[0][-1:]
    mudflow_dir = 'data/mudflow/process_' + process_num + '/'
    if not os.path.exists(mudflow_dir):
        os.mkdir(mudflow_dir)
    # create csv to keep track of processed apks
    

    df = pd.read_table(apks_csv_path, sep=" ", header=None)
    # for each apk category (malware, bening, gp), get list of apks and process them
    for i in range(len(df)):
        apks = df.iloc[i]
        for apk in apks:
            process_apk(apk)
