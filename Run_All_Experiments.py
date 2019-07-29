import csv
import glob
from Main import create_mudflow_file
from multiprocessing import Process
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
    file.close()


def create_apks_chunks(num_workers):
    general_malware = [f for f in glob.glob(apk_files_dir + 'malware/**/*.apk', recursive=True)]
    general_benign = [f for f in glob.glob(apk_files_dir + 'benign/**/*.apk', recursive=True)]
    gp_malware = [f for f in glob.glob(apk_files_dir + 'gp/**/*.apk', recursive=True)]

    general_malware_chunks = split(general_malware, num_workers)
    general_benign_chunks = split(general_benign, num_workers)
    gp_malware_chunks = split(gp_malware, num_workers)

    for i in range(num_workers):
        create_csv(general_malware_chunks[i], general_benign_chunks[i], gp_malware_chunks[i], i)

def start_experiments(apks):
    #create_susi_categories_file(apk_list_csv_dir + 'apks_chunk_' + str(i) + '.csv')
    create_mudflow_file(apks)


def update_apks_processed():
    apks_processed_files = [i for i in glob.glob('data/mudflow/**/apks_processed.csv', recursive=True)]
    if apks_processed_files:
        result = pd.concat([pd.read_csv(f) for f in apks_processed_files]).drop_duplicates(keep='last')
        combined_csv = pd.DataFrame(result)
    for apks_processed_file in apks_processed_files:
        combined_csv.to_csv(apks_processed_file, index=False, encoding='utf-8-sig')


def main():
    num_workers = 3
    #num_workers = int(sys.argv[1])
    create_apks_chunks(num_workers)
    update_apks_processed()

    procs = []

    for i in range(num_workers):
        apk_list_csv_path = apk_list_csv_dir + 'apks_chunk_' + str(i) + '.csv'
        p = Process(target=start_experiments, args=[apk_list_csv_path])
        procs.append(p)
        p.start()
    for p in procs:
        p.join



if __name__ =='__main__':
    main()