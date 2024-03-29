import os
import re
import shutil
import uuid
import pandas as pd
from pandas import DataFrame
from utilities import append_df_to_excel

mudflow_count_apks = 0
mudflow_file_path = ''


def create_new_file(pid):
    global mudflow_file_path
    mudflow_file_path = 'data/mudflow/process_' + str(pid) + '/new_' + str(uuid.uuid4().hex) + '.xlsx'
    shutil.copy('data/Column_Names.xlsx', mudflow_file_path)


#   Add triangular brackets to match flowdroid formatting when it logs flows
def process_column_name(column_name):
    flow = [x.strip() for x in column_name.split('->')]
    if flow and len(flow) == 2:
        source = flow[0]
        sink = flow[1]
        if flow[0] != 'NO_SENSITIVE_SOURCE':
            source = '<' + flow[0] + '>'
        if flow[1] != 'NO_SENSITIVE_SINK':
            sink = '<' + flow[1] + '>'
        return source + ' -> ' + sink
    return column_name


def calc_num_flows(apk, column_name):
    flow = process_column_name(column_name)
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    count_flows = 0
    with open(output_path, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if flow in line:
                count_flows += 1
    return int(count_flows)


def update_row_data(apk, has_flow):
    columns = pd.read_excel(mudflow_file_path, sheet_name='Sheet1').columns
    data = []
    for i in range(len(columns)):
        if columns[i].lower().strip() == 'name':
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
                data.append(int(year[0]))
            else:
                data.append('')
        elif columns[i].lower().strip() == 'category':
            if 'GeneralBenign' in apk:
                data.append('general benign')
            elif 'GeneralMalware' in apk:
                data.append('general malware')
            elif 'GPMalware' in apk:
                data.append('gp malware')
            else:
                data.append('')
        elif not has_flow:
            data.append(0)
        else:
            data.append(calc_num_flows(apk, columns[i]))

    df = DataFrame(data).T
    append_df_to_excel(mudflow_file_path, df, header=None)


def add_data_to_mudflow_file(apk, pid, has_flow):
    global mudflow_count_apks
    global mudflow_file_path
    # create new excel sheet if count is equal to 0 or max number of rows
    if mudflow_count_apks == 0:
        create_new_file(pid)
    if mudflow_count_apks >= 99:
        mudflow_count_apks = 0
        create_new_file(pid)
    update_row_data(apk, has_flow)
    mudflow_count_apks += 1
