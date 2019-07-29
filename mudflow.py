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
    filePath = 'data/mudflow/process_' + str(pid) + '/' + str(uuid.uuid4().hex) + '.xlsx'
    shutil.copy('data/Column_Names.xlsx', filePath)


def parse_result(output_path, flow):
    with open(output_path, 'r', errors='ignore') as file:
        with open(output_path, 'r') as file:
            contents = file.read()
            if flow in contents:
                print(flow + ' in contents')
            else:
                return 0


def num_flows(apk, flow, map):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    with open(output_path, 'r') as file:
        contents = file.read()
        if flow.strip() not in contents:
            return 0
    source_and_sink = [x.strip() for x in flow.split('->')]
    if source_and_sink and len(source_and_sink) == 2:
        source = source_and_sink[0].strip()
        sink = source_and_sink[1].strip()
        sources = map.get(sink)
        count_flow = 0
        if sources:
            for s in sources:
                if s == source:
                    count_flow += 1
    return int(count_flow)



def update_row_data(apk, pid, has_flow, map):
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
            data.append(num_flows(apk, columns[i], map))

    df = DataFrame(data).T
    append_df_to_excel(filePath, df, header=None)


def contains_sink(line):
    return 'was called with values from the following sources' in line


def contains_source(line):
    return ' - - ' in line


def parse_sink(line):
    p = r'(?<=The sink ).+(?= in method )'
    s1 = re.findall(p, line)[0]
    s2 = s1.split('<')[1]
    return '<' + s2


def parse_source(line):
    p = r'(?<= - - ).+(?= in method )'
    s1 = re.findall(p, line)[0]
    s2 = s1.split('<')[1]
    return '<' + s2


def create_source_sink_map(apk):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    map = {}
    sink = ''
    sources = []
    collecting_sources = False
    with open(output_path, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if contains_sink(line):
                if collecting_sources:
                    map[sink] = sources
                    sources = []
                sink = parse_sink(line)
                collecting_sources = True
            elif contains_source(line) and collecting_sources:
                sources.append(parse_source(line))
            elif collecting_sources:
                map[sink] = sources
                sources = []
                collecting_sources = False

    #for key, value in map.items():
    #    print(key)
    #    for i in range(len(value)):
    #        print('--> ' + value[i])
    return map




def add_data_to_mudflow_file(apk, pid, has_flow):
    global count
    global filePath
    map = create_source_sink_map(apk)
    # create new excel sheet if count = 0 or max number of rows
    if count == 0:
        create_new_file(pid)
    if count >= 5:  # TODO: Change to 99 later
        count = 0
        create_new_file(pid)
    update_row_data(apk, pid, has_flow, map)
    count = count + 1