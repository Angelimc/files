import csv
import glob
import os
import sys
import time
from utilities import add_to_error_list, append_df_to_excel
from flowdroid import run_flowdroid
from multiprocessing import Process
from mudflow import add_data_to_mudflow_file
import pandas as pd
from susi import add_data_to_susi_file
from datetime import datetime

#   TODO:
# Testing in zeus: apk_files_dir = 'data/'
# Zeus: apk_files_dir = '/data/michaelcao/DatasetsForTools/'
# Thanos: apk_files_dir = '/nfs/zeus/michaelcao/DatasetsForTools/'
# Local: apk_files_dir ='/Users/angeli/My_Documents/Mudflow/DataTest/'
apk_files_dir = '/Users/angeli/My_Documents/Mudflow/DataTest/'


def split(l, n):
    k, m = divmod(len(l), n)
    return list((l[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)))


def create_csv(general_malware, general_benign, gp_malware, i):
    with open('data/apks_chunk_' + str(i) + '.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(general_malware)
        writer.writerow(general_benign)
        writer.writerow(gp_malware)


def create_apks_chunks(num_workers):
    general_malware = [f for f in glob.glob(apk_files_dir + 'GeneralMalware/**/*.apk', recursive=True)]
    general_benign = [f for f in glob.glob(apk_files_dir + 'GeneralBenign/**/*.apk', recursive=True)]
    gp_malware = [f for f in glob.glob(apk_files_dir + 'GPMalware/**/*.apk', recursive=True)]

    general_malware_chunks = split(general_malware, num_workers)
    general_benign_chunks = split(general_benign, num_workers)
    gp_malware_chunks = split(gp_malware, num_workers)

    for i in range(num_workers):
        create_csv(general_malware_chunks[i], general_benign_chunks[i], gp_malware_chunks[i], i)


#   Creates folders and file for list of processed apks for each worker if they don't exist
#   @param id: number to identify this for this worker
def setup_folders(pid):
    mudflow_dir = 'data/mudflow/process_' + pid + '/'
    if not os.path.exists(mudflow_dir):
        os.mkdir(mudflow_dir)
    susi_dir = 'data/susi/process_' + pid + '/'
    if not os.path.exists(susi_dir):
        os.mkdir(susi_dir)
    if not os.path.exists('data/progress/apks_processed_' + pid + '.csv'):
        with open('data/progress/apks_processed_' + pid + '.csv', 'w') as f1:
            pass


#   Returns true if apk has been processed by this worker
#   @param id: number to identify this for this worker
#   @param current apk path being processed
def is_processed(pid, apk):
    with open('data/progress/apks_processed_' + pid + '.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            for i in range(len(row)):
                if os.path.splitext(os.path.basename(apk))[0] in row[i]:
                    print('Already processed: ' + apk)
                    return True
        return False


#   Add apk to to list of processed apks
#   @param current apk path being processed
#   @param id: number to identify this for this worker
def add_to_processed_apks_list(apk, pid, start_time, end_time):
    with open('data/progress/apks_processed_' + pid + '.csv', 'a') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([apk + '_' + start_time.strftime("%Y%m%d-%H%M%S") + '_' + end_time.strftime("%Y%m%d-%H%M%S")])
    print('Worker ' + str(pid) + ' completed processing: ' + apk)


def add_data_to_time_file(apk, pid, start_time, end_time, no_source, no_sink, no_result, has_exception):
    tdelta = end_time - start_time
    data = [os.path.basename(apk), start_time.strftime("%Y%m%d-%H%M%S"), end_time.strftime("%Y%m%d-%H%M%S"),
            tdelta.seconds, tdelta.seconds / 60, no_source, no_sink, no_result, has_exception]
    df = pd.DataFrame(data).T
    append_df_to_excel('data/progress/apks_time_' + pid + '.xlsx', df, header=None)


def update_apks_processed(num_workers):
    apks_processed_files = [i for i in glob.glob('data/progress/apks_processed_*.csv')]
    if apks_processed_files:
        print('Combining processed apks list')
        try:
            result = pd.concat([pd.read_csv(f) for f in apks_processed_files])
            combined_csv = pd.DataFrame(result).drop_duplicates(keep='last')
            for pid in range(num_workers):
                combined_csv.to_csv('data/progress/apks_processed_' + str(pid) + '.csv', index=False,
                                    encoding='utf-8-sig')
        except ValueError:
            pass


#   Return False if flowdroid output contains 'No sources found', 'No sinks found', or 'No results found', True
#   otherwise
def has_flow(apk, pid, start_time, end_time):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    with open(output_path, 'r') as file:
        contents = file.read()
        if 'No sources found' in contents:
            add_data_to_time_file(apk, pid, start_time, end_time, 1, 0, 0, 0)
            print('No sources found for ' + apk)
            return False
        if 'No sinks found' in contents:
            add_data_to_time_file(apk, pid, start_time, end_time, 0, 1, 0, 0)
            print('No sinks found for ' + apk)
            return False
        if 'No results found' in contents:
            add_data_to_time_file(apk, pid, start_time, end_time, 0, 0, 1, 0)
            print('No results found for ' + apk)
            return False
    add_data_to_time_file(apk, pid, start_time, end_time, 0, 0, 0, 0)
    return True


def contains_error(apk, pid):
    output_path = 'data/log/' + os.path.splitext(os.path.basename(apk))[0] + '.txt'
    if not os.path.exists(output_path):
        add_to_error_list(apk, pid, 'flowdroid', 'flowdroid text file output does not exist: ' + output_path)
        return True
    with open(output_path, 'r') as file:
        contents = file.read()
        if 'Exception in thread ' in contents:
            add_to_error_list(apk, pid, 'flowdroid', 'Flowdroid Runtime Error')
            return True
        return False


def start_experiment(apks_list_path):
    pid = os.path.splitext(apks_list_path)[0][-1:]
    setup_folders(pid)
    with open(apks_list_path, 'r') as f:
        apks_list = csv.reader(f, delimiter=',')
        for apks in apks_list:
            for i in range(len(apks)):
                if not is_processed(pid, apks[i]):
                    print('Worker ' + str(pid) + ' processing: ' + apks[i])
                    start_time = datetime.now()
                    run_flowdroid(apks[i])
                    end_time = datetime.now()
                    if contains_error(apks[i], pid):
                        add_to_processed_apks_list(apks[i], pid, start_time, end_time)
                        add_data_to_time_file(apks[i], pid, start_time, end_time, 0, 0, 0, 1)
                        continue
                    contain_flow = has_flow(apks[i], pid, start_time, end_time)
                    if contain_flow:
                        add_data_to_susi_file(apks[i], pid)
                    add_data_to_mudflow_file(apks[i], pid, contain_flow)
                    add_to_processed_apks_list(apks[i], pid, start_time, end_time)


#   Runs flowdroid on all apks and creates the susi and mudflow excel sheets using given number of processes
#   @param: number of processes to run
def main():
    #num_workers = int(sys.argv[1])
    num_workers = 1
    update_apks_processed(num_workers)
    create_apks_chunks(num_workers)
    procs = []
    for i in range(num_workers):
        apk_list_csv_path = 'data/apks_chunk_' + str(i) + '.csv'
        p = Process(target=start_experiment, args=[apk_list_csv_path])
        procs.append(p)
        p.start()
    for p in procs:
        p.join()


if __name__ == '__main__':
    main()
