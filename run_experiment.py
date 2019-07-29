import csv
import glob
import os

from pandas.errors import EmptyDataError

from Utilities import add_to_error_list
from flowdroid import run_flowdroid
from multiprocessing import Process
from mudflow import add_data_to_mudflow_file, create_source_sink_map
import pandas as pd

"""
Get list of apks for:
General benign
Malware
GP
- only include if not duplicated
arranged by name

1  csv for each process

For each process:
    give csv
    create file for outp

"""
# TODO: Ask what to do with 0 flows
#TODO: change directories
apk_files_dir = '/Users/angeli/My_Documents/Mudflow/DataTest/'
apk_list_csv_dir = '/Users/angeli/My_Documents/Mudflow/'


def split(l, n):
    k, m = divmod(len(l), n)
    return list((l[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)))


def create_csv(general_malware, general_benign, gp_malware, i):
    with open(apk_list_csv_dir + 'apks_chunk_' + str(i) + '.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(general_malware)
        writer.writerow(general_benign)
        writer.writerow(gp_malware)


def create_apks_chunks(num_workers):
    general_malware = [f for f in glob.glob(apk_files_dir + 'malware/**/*.apk', recursive=True)]
    general_benign = [f for f in glob.glob(apk_files_dir + 'benign/**/*.apk', recursive=True)]
    gp_malware = [f for f in glob.glob(apk_files_dir + 'gp/**/*.apk', recursive=True)]

    general_malware_chunks = split(general_malware, num_workers)
    general_benign_chunks = split(general_benign, num_workers)
    gp_malware_chunks = split(gp_malware, num_workers)

    for i in range(num_workers):
        create_csv(general_malware_chunks[i], general_benign_chunks[i], gp_malware_chunks[i], i)


#   Creates folders and file for list of processed apks for each worker if they don't exist
#   @param id: number to identify this for this worker
def setup_folders(id):
    mudflow_dir = 'data/mudflow/process_' + id + '/'
    if not os.path.exists(mudflow_dir):
        os.mkdir(mudflow_dir)
    susi_dir = 'data/susi/process_' + id + '/'
    if not os.path.exists(susi_dir):
        os.mkdir(susi_dir)
    if not os.path.exists('data/progress/apks_processed_' + id + '.csv'):
        with open('data/progress/apks_processed_' + id + '.csv', 'w') as f1:
            pass


#   Returns true if apk has been processed by this worker
#   @param id: number to identify this for this worker
#   @param current apk path being processed
def is_processed(pid, apk):
    # return if apk has already been processed
    with open('data/progress/apks_processed_' + pid + '.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            for i in range(len(row)):
                if os.path.splitext(os.path.basename(apk))[0] in row[i]:
                    print('already processed: ' + apk)
                    return True
        print('processing: ' + apk)
        return False


#   Add apk to to list of processed apks
#   @param current apk path being processed
#   @param id: number to identify this for this worker
def add_to_processed_apks_list(apk, id):
    with open('data/progress/apks_processed_' + id + '.csv', 'a') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([apk])


def update_apks_processed(num_workers):
    apks_processed_files = [i for i in glob.glob('data/progress/apks_processed_*.csv')]
    if apks_processed_files:
        try:
            result = pd.concat([pd.read_csv(f) for f in apks_processed_files])
            combined_csv = pd.DataFrame(result).drop_duplicates(keep='last')
            for pid in range(num_workers):
                combined_csv.to_csv('data/progress/apks_processed_' + str(pid) + '.csv', index=False, encoding='utf-8-sig')
        except EmptyDataError:
            df = pd.DataFrame()


def has_flow(apk):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    with open(output_path, 'r') as file:
        contents = file.read()
        if 'No sources found' in contents or 'No sinks found' in contents or 'No results found' in contents:
            print('no sources or sinks found')
            return True
    return False


def contains_error(apk, pid):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    if os.path.exists(output_path):
        with open(output_path, 'r') as file:
            contents = file.read()
            if 'Exception in thread ' in contents:
                add_to_error_list(apk, pid, 'flowdroid', 'Flowdroid Runtime Error')
        return True
    else:
        add_to_error_list(apk, pid, 'flowdroid', 'flowdroid text file output does not exist: ' + output_path)


def start_experiment(apks_list_path):
    pid = os.path.splitext(apks_list_path)[0][-1:]
    setup_folders(pid)
    with open(apks_list_path, 'r') as f:
        apks_list = csv.reader(f, delimiter=',')
        for apks in apks_list:
            for i in range(len(apks)):
                if not is_processed(pid, apks[i]):
                    #run_flowdroid(apks[i])
                    if not contains_error(apks[i], pid):
                        add_to_processed_apks_list(apks[i], pid)
                        continue
                    contain_flow = has_flow(apks[i])
                    if contain_flow:
                        pass
                        # add_data_to_susi_file(apks[i])
                    add_data_to_mudflow_file(apks[i], pid, contain_flow)
                    add_to_processed_apks_list(apks[i], pid)


def main():
    num_workers = 1
    #num_workers = int(sys.argv[1])
    create_apks_chunks(num_workers)
    update_apks_processed(num_workers)
    procs = []
    for i in range(num_workers):
        apk_list_csv_path = apk_list_csv_dir + 'apks_chunk_' + str(i) + '.csv'
        p = Process(target=start_experiment, args=[apk_list_csv_path])
        procs.append(p)
        p.start()
    for p in procs:
        p.join()


if __name__ =='__main__':
    main()