import multiprocessing as mp
import glob
import os
import shutil
import uuid
import pandas as pd
from pandas import DataFrame

from Utilities import append_df_to_excel, copyToFile, appendToFile
from flowdroid import run_flowdroid
import csv
import re

id = None
mudflow_dir = ''
fileWithColumnNames = '/Users/angeli/PycharmProjects/mudflow/data/Column_Names.xlsx'
count = 0
filePath = ''


def create_new_file():
    global filePath
    unique_id = str(uuid.uuid4().hex)
    filePath = mudflow_dir + str(uuid.uuid4().hex) + '.xlsx'
    shutil.copy('data/Column_Names.xlsx', filePath)


def run_flowdroid_all_columns(apk):
    cols = pd.read_excel(filePath, sheet_name='Sheet1').columns
    data = []
    for i in range(len(5)):
        if i == 0:
            continue
        elif cols[i].lower() == 'name':
            data.append(apk)
        elif cols[i].lower() == 'year':
            p = r'(?<=\/)\d{4}(?=\/)'
            year = re.findall(p, apk)
            if year:
                data.append(year[0])
            else:
                data.append('')
        elif cols[i].lower() == 'category':
            if 'GeneralBenign' in apk:
                data.append(0)
            elif 'GeneralMalware' in apk or 'GPMalware' in apk:
                data.append(1)
            else:
                data.append('')
        else:
            # extract source and sink
            column_name = [x.strip() for x in cols[i].split('->')]
            if column_name and len(column_name) == 2:
                addSource(column_name[0])
                addSink(column_name[1])
                # add number of leaks to row
                numLeaks = run_flowdroid(apk, 'SourcesAndSinks.txt')
                data.append(numLeaks)
                print(cols[i] + ': ' + str(numLeaks))
            else:
                data.append('')
    df = DataFrame(data).T
    append_df_to_excel(filePath, df, header=None)

def process_apk(apk):
    global count
    global filePath
    # return if apk has already been processed
    with open(mudflow_dir + 'apks_processed.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if os.path.splitext(os.path.basename(apk))[0] in row:
                return

    # create new excel sheet if it reaches max num of rows
    if count == 0:
        create_new_file()
    if count >= 2: # TODO: Change to 99 later
        count = 0
        create_new_file()
    run_flowdroid_all_columns(apk)
    count = count + 1

    # add apk to apks_processed file
    with open(mudflow_dir + 'apks_processed.csv', 'a') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([apk])


def create_mudflow_file(apks_csv_path):
    global mudflow_dir
    # create a directory for each process
    id = os.path.splitext(apks_csv_path)[0][-1:]
    mudflow_dir = 'data/mudflow/process_' + id + '/'
    if not os.path.exists(mudflow_dir):
        os.mkdir(mudflow_dir)

    if not os.path.exists(mudflow_dir + 'apks_processed.csv'):
        with open(mudflow_dir + 'apks_processed.csv', 'w') as f1:
            pass

    with open(apks_csv_path, 'r') as f:
        mycsv = csv.reader(f, delimiter=',')
        for apks in mycsv:
            for i in range(len(apks)):
                process_apk(apks[i])