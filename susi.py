import os
import uuid
from pandas import DataFrame
from utilities import append_df_to_excel

susi_categories = ['HARDWARE_INFO', 'UNIQUE_IDENTIFIER', 'LOCATION_INFORMATION', 'NETWORK_INFORMATION',
                    'ACCOUNT_INFORMATION', 'EMAIL', 'FILE_INFORMATION', 'BLUETOOTH_INFORMATION', 'VOIP',
                    'DATABASE_INFORMATION', 'PHONE_INFORMATION', 'AUDIO', 'SMS_MMS', 'CONTACT_INFORMATION',
                    'CALENDAR_INFORMATION', 'SYSTEM_SETTINGS', 'IMAGE', 'BROWSER_INFORMATION', 'NFC',
                    'NO_SENSITIVE_SOURCE', 'CONTENT_RESOLVER']
susi_count_apks = 0
susi_file_path = ''


def create_new_file_path(pid):
    global susi_file_path
    susi_file_path = 'data/susi/process_' + str(pid) + '/' + str(uuid.uuid4().hex) + '.xlsx'


def parse_source(line):
    flow = [x.strip() for x in line.split('->')]
    return flow[0]


def process_apk(apk):
    global susi_categories
    global susi_file_path
    apk_categories = []
    duplicate_apk_names = []
    for susi_category in susi_categories:
        if susi_category not in apk_categories:
            output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
            with open(output_path, 'r') as f:
                lines = f.read().splitlines()
                for line in lines:
                    if ' -> ' not in line:
                        continue
                    source = parse_source(line)
                    with open('sources_sinks_categories/' + susi_category + '.txt', 'r') as file:
                        contents = file.read()
                        if susi_category not in apk_categories and source in contents:
                            apk_categories.append(susi_category)
                            duplicate_apk_names.append(os.path.basename(apk))
    df = DataFrame({'A': duplicate_apk_names, 'B': apk_categories})
    append_df_to_excel(susi_file_path, df, header=None)


def add_data_to_susi_file(apk, pid):
    global susi_count_apks
    global susi_file_path
    # create new excel sheet if count is equal to 0 or max num of apks
    if susi_count_apks == 0:
        create_new_file_path(pid)
    if susi_count_apks >= 99:
        susi_count_apks = 0
        create_new_file_path(pid)
    process_apk(apk)
    susi_count_apks += 1


