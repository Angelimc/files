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


def num_sensitive_flows(sink_map, source_map, column_source, column_sink):
    count_flow = 0
    if column_source == 'NO_SENSITIVE_SOURCE':
        # get all the sources that lead to the sink
        parsed_sources = sink_map.get(column_sink)
        if parsed_sources:
            for parsed_source in parsed_sources:
                with open('sources_sinks_categories/no_sensitive_source.txt', 'r') as file:
                    list_not_sensitive_source = file.read()
                    if parsed_source in list_not_sensitive_source:
                        count_flow += 1
        return int(count_flow)
    elif column_sink == 'NO_SENSITIVE_SINK':
        parsed_sinks = source_map.get(column_source)
        if parsed_sinks:
            for parsed_sink in parsed_sinks:
                with open('sources_sinks_categories/no_sensitive_sink.txt', 'r') as file:
                    list_not_sensitive_sink = file.read()
                    if parsed_sink in list_not_sensitive_sink:
                        count_flow += 1
    return int(count_flow)


def calc_num_flows(apk, flow, sink_map, source_map):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    with open(output_path, 'r') as file:
        contents = file.read()
        if flow.strip() not in contents:
            return 0
    column_name = [x.strip() for x in flow.split('->')]
    count_flow = 0
    if column_name and len(column_name) == 2:
        source = column_name[0].strip()
        sink = column_name[1].strip()
        if source == 'NO_SENSITIVE_SOURCE' or sink == 'NO_SENSITIVE_SINK':
            return num_sensitive_flows(sink_map, source_map, source, sink)
        sources = sink_map.get(sink)
        if sources:
            for s in sources:
                if s == source:
                    count_flow += 1
    return int(count_flow)


def update_row_data(apk, pid, has_flow, sink_map, source_map):
    columns = pd.read_excel(filePath, sheet_name='Sheet1').columns
    data = []
    for i in range(len(columns)):
        if i == 0:
            continue
        elif columns[i].lower().strip() == 'name':
            data.append(os.path.splitext(os.path.basename(apk))[0])
        elif columns[i].lower().strip() == 'malicious':
            if 'GeneralBenign' in apk:
                data.append(0)
            elif 'GeneralMalware' in apk or 'GPMalware' in apk:
                data.append(1)
            else:
                data.append('')
        elif columns[i].lower().strip() == 'year':
            p = r'(?<=\/)\d{4}(?=\/)'
            year = re.findall(p, apk)
            if year:
                data.append(year[0])
            else:
                data.append('')
        elif not has_flow:
            data.append(0)
        else:
            data.append(calc_num_flows(apk, columns[i], sink_map, source_map))

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


def create_sink_source_map(apk):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    sink_map = {}
    source_map = {}
    sink = ''
    sources = []
    collecting_sources = False
    with open(output_path, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if contains_sink(line):
                if collecting_sources:
                    # add to map where sink is the key and sources are the values
                    sink_map[sink] = sources
                    # add to map where source is the key and sinks are the values
                    for s in sources:
                        if s in source_map:
                            source_map[s].append(sink)
                        else:
                            source_map[s] = [sink]
                    sources = []
                sink = parse_sink(line)
                collecting_sources = True
            elif contains_source(line) and collecting_sources:
                sources.append(parse_source(line))
            elif collecting_sources:
                sink_map[sink] = sources
                for s in sources:
                    if s in source_map:
                        source_map[s].append(sink)
                    else:
                        source_map[s] = [sink]
                sources = []
                collecting_sources = False

    #for key, value in map.items():
    #    print(key)
    #    for i in range(len(value)):
    #        print('--> ' + value[i])
    return sink_map, source_map


def add_data_to_mudflow_file(apk, pid, has_flow):
    global count
    global filePath
    sink_map, source_map = create_sink_source_map(apk)
    # create new excel sheet if count = 0 or max number of rows
    if count == 0:
        create_new_file(pid)
    if count >= 5:  # TODO: Change to 99 later
        count = 0
        create_new_file(pid)
    update_row_data(apk, pid, has_flow, sink_map, source_map)
    count = count + 1