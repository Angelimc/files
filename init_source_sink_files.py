import re
from susi import susi_categories

#   Create source or sink files with methods converted to flowdroid input format
from utilities import copy_to_file, append_to_file


def create_source_sink_file(input_file, output_file, is_source):
    with open(input_file) as f1:
        lines = f1.readlines()
        sources = []
        # check if line contains method signature
        pattern = re.compile(r'<.+\)>')
        for line in lines:
            res = pattern.findall(line)
            if res:
                # convert to flowdroid format for source or sink
                if is_source:
                    sources.append(res[0] + ' -> _SOURCE_')
                else:
                    sources.append(res[0] + ' -> _SINK_')
    with open(output_file, 'w') as f2:
        f2.write('\n'.join(sources))
    stype = 'sinks'
    if is_source:
        stype = 'sources'
    print('Num of all ' + stype + ': ' + str(len(sources)))


def create_susi_category(category):
    with open('sources_sinks_categories/SourcesAll.txt') as f1:
        lines = f1.readlines()
        sources = []
        # check if line contains method signature for given susi category
        pattern = re.compile(r'<.+\)>.+\(' + re.escape(category) + r'\)')
        for line in lines:
            if pattern.match(line):
                # convert to flowdroid log output format
                p2 = re.compile(r'<.+\)>')
                res = p2.findall(line)
                if res:
                    sources.append(res[0])
    with open('sources_sinks_categories/' + category + '.txt', 'w') as f2:
        f2.write('\n'.join(sources))
        print('Created text file for ' + category + ' with ' + str(len(sources)) + ' sources')


def main():
    print('Creating a text file with all api for each susi category')
    for category in susi_categories:
        if category != 'NO_SENSITIVE_SOURCE':
            create_susi_category(category)
    print('Creating a sources and  sinks file')
    create_source_sink_file('sources_sinks_categories/SinksAll.txt', 'sources_sinks_categories/FormattedSinksAll.txt',
                            True)
    create_source_sink_file('sources_sinks_categories/SourcesAll.txt',
                            'sources_sinks_categories/FormattedSourcesAll.txt', False)
    copy_to_file('sources_sinks_categories/FormattedSourcesAll.txt', 'SourcesAndSinks.txt')
    append_to_file('sources_sinks_categories/FormattedSinksAll.txt', 'SourcesAndSinks.txt')


if __name__ == '__main__':
    main()
