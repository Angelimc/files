#!/usr/bin/python

import re

apkPath = '/Users/angeli/My_Documents/Mudflow/apks'
# Excludes NO_SENSITIVE_SOURCE, which has a different implementation for creating files
sourceCategories = ['HARDWARE_INFO', 'UNIQUE_IDENTIFIER', 'LOCATION_INFORMATION', 'NETWORK_INFORMATION',
                    'ACCOUNT_INFORMATION', 'EMAIL', 'FILE_INFORMATION', 'BLUETOOTH_INFORMATION', 'VOIP',
                    'DATABASE_INFORMATION', 'PHONE_INFORMATION', 'AUDIO', 'SMS_MMS', 'CONTACT_INFORMATION',
                    'CONTENT_RESOLVER', 'CALENDAR_INFORMATION', 'SYSTEM_SETTINGS', 'IMAGE', 'BROWSER_INFORMATION', 'NFC']


def copyToFile(input, output):
    with open(input) as f1:
        with open(output, 'w') as f2:
            for line in f1:
                f2.write(line)
            f2.write('\n')


def appendToFile(input, output):
    with open(input) as f1:
        with open(output, 'a+') as f2:
            for line in f1:
                f2.write(line)


def createSourceSinkForCategory(category):
    print(category)
    with open('sourceSinkFiles/SourcesAll.txt') as f1:
        lines = f1.readlines()
        sources = []
        # check if line contains method signature for given susi category
        pattern = re.compile(r'<.+\)>.+\(' + re.escape(category) + r'\)')
        for line in lines:
            if pattern.match(line):
                # convert to flowdroid format for source
                p2 = re.compile(r'<.+\)>')
                res = p2.findall(line)
                if res:
                    sources.append(res[0] + ' -> _SOURCE_')
    # write sources and ALL_SINKS to file
    copyToFile('sourceSinkFiles/ALL_SINKS.txt', 'sourceSinkFiles/both/' + category + '.txt')
    with open('sourceSinkFiles/both/' + category + '.txt', 'a+') as f2:
        f2.write('\n'.join(sources))
    print(len(sources))


def createSourceOrSink(input, output, isSource):
    print(output)
    with open(input) as f1:
        lines = f1.readlines()
        sources = []
        # check if line contains method signature
        pattern = re.compile(r'<.+\)>')
        for line in lines:
            res = pattern.findall(line)
            if res:
                # convert to flowdroid format for source or sink
                if isSource:
                    sources.append(res[0] + ' -> _SOURCE_')
                else:
                    sources.append(res[0] + ' -> _SINK_')
    with open(output, 'w') as f2:
        f2.write('\n'.join(sources))
    print(len(sources))


# create NO_SENSITIVE_SOURCE from NO_CATEGORY
def createNoSensitiveSource():
    print('no sensitive source')
    with open('sourceSinkFiles/SourcesAll.txt') as f1:
        lines = f1.readlines()
        sources = []
        # check if line contains method signature for given susi category
        pattern = re.compile(r'<.+\)>.+\(NO_CATEGORY\)')
        for line in lines:
            if pattern.match(line):
                # convert to flowdroid format for source
                p2 = re.compile(r'<.+\)>')
                res = p2.findall(line)
                if res:
                    sources.append(res[0] + ' -> _SOURCE_')
    # write sources and ALL_SINKS to file
    with open('sourceSinkFiles/NO_SENSITIVE_SOURCE.txt', 'w') as f2:
        f2.write('\n'.join(sources))
    print(len(sources))


# create NO_SENSITIVE_SINK from NO_CATEGORY
def createNoSensitiveSink():
    print('no sensitive sink')
    with open('sourceSinkFiles/SinksAll.txt') as f1:
        lines = f1.readlines()
        sinks = []
        # check if line contains method signature for given susi category
        pattern = re.compile(r'<.+\)>.+\(NO_CATEGORY\)')
        for line in lines:
            if pattern.match(line):
                # convert to flowdroid format for source
                p2 = re.compile(r'<.+\)>')
                res = p2.findall(line)
                if res:
                    sinks.append(res[0] + ' -> _SINK_')
    # write sources and ALL_SINKS to file
    with open('sourceSinkFiles/NO_SENSITIVE_SINK.txt', 'w') as f2:
        f2.write('\n'.join(sinks))
    print(len(sinks))


def createSourceSinkFiles():
    createSourceOrSink('sourceSinkFiles/SinksAll.txt', 'sourceSinkFiles/ALL_SINKS.txt', False)
    createSourceOrSink('sourceSinkFiles/Not_Sensitive_Sink.txt', 'sourceSinkFiles/NO_SENSITIVE_SINK.txt', False)
    createSourceOrSink('sourceSinkFiles/Not_Sensitive_Source.txt', 'sourceSinkFiles/NO_SENSITIVE_SOURCE.txt', True)
    #createNoSensitiveSource()
    #createNoSensitiveSink()
    copyToFile('sourceSinkFiles/NO_SENSITIVE_SOURCE.txt', 'sourceSinkFiles/both/NO_SENSITIVE_SOURCE.txt')
    appendToFile('sourceSinkFiles/ALL_SINKS.txt', 'sourceSinkFiles/both/NO_SENSITIVE_SOURCE.txt')

    for category in sourceCategories:
        createSourceSinkForCategory(category)


#createSourceSinkFiles()