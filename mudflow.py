import multiprocessing as mp
import glob
import os
import shutil
import uuid
import pandas as pd
from pandas import DataFrame

from Utilities import append_df_to_excel, copyToFile, appendToFile, add_to_error_list
from flowdroid import run_flowdroid
import csv
import re

count = 0
filePath = ''


def create_new_file(pid):
    global filePath
    unique_id = str(uuid.uuid4().hex)
    filePath = 'data/mudflow/process_' + str(pid) + str(uuid.uuid4().hex) + '.xlsx'
    shutil.copy('data/Column_Names.xlsx', filePath)


def parse_result(output_path, flow):
    with open(output_path, 'r', errors='ignore') as file:
        with open(output_path, 'r') as file:
            contents = file.read()
            if flow in contents:
                print(flow + ' in contents')
            else:
                return 0


def update_row_data(apk, pid, has_flow):
    columns = pd.read_excel(filePath, sheet_name='Sheet1').columns
    data = []
    for i in range(5):
        if i == 0:
            continue
        elif columns[i].lower() == 'name':
            data.append(apk)
        elif columns[i].lower() == 'malicious':
            if 'GeneralBenign' in apk:
                data.append(0)
            elif 'GeneralMalware' in apk or 'GPMalware' in apk:
                data.append(1)
            else:
                data.append('')
        elif columns[i].lower() == 'year':
            p = r'(?<=\/)\d{4}(?=\/)'
            year = re.findall(p, apk)
            if year:
                data.append(year[0])
            else:
                data.append('')
        elif not has_flow:
            data.append(0)
        else:
            # extract source and sink
            output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
            """
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
            """
    df = DataFrame(data).T
    append_df_to_excel(filePath, df, header=None)


def create_source_sink_map(apk):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'


def add_data_to_mudflow_file(apk, pid, has_flow):
    global count
    global filePath
    map = create_source_sink_map(apk)
    # create new excel sheet if count = 0 or max number of rows
    if count == 0:
        create_new_file(pid)
    if count >= 2:  # TODO: Change to 99 later
        count = 0
        create_new_file(pid)
    update_row_data(apk, pid, has_flow)
    count = count + 1