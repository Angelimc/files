import os

from pandas import DataFrame

sourceCategories = ['HARDWARE_INFO', 'UNIQUE_IDENTIFIER', 'LOCATION_INFORMATION', 'NETWORK_INFORMATION',
                    'ACCOUNT_INFORMATION', 'EMAIL', 'FILE_INFORMATION', 'BLUETOOTH_INFORMATION', 'VOIP',
                    'DATABASE_INFORMATION', 'PHONE_INFORMATION', 'AUDIO', 'SMS_MMS', 'CONTACT_INFORMATION',
                    'CALENDAR_INFORMATION', 'SYSTEM_SETTINGS', 'IMAGE', 'BROWSER_INFORMATION', 'NFC',
                    'NO_SENSITIVE_SOURCE', 'CONTENT_RESOLVER']


def parse_source(line):
    flow = [x.strip() for x in line.split('->')]
    return flow[0]


def add_data_to_susi_file(apk):
    susi_categories = []
    for category in sourceCategories:
        output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
        count_flows = 0
        with open(output_path, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                if ' -> ' not in line:
                    continue
                source = parse_source(line)
                with open('sources_sinks_categories/' + category + '.txt', 'r') as file:
                    contents = file.read()
                    if source in contents:
                        susi_categories.append(category)
                        
