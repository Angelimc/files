import csv
import glob
import sys
from Main import create_mudflow_file

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
    general_malware = [f for f in glob.glob(apk_files_dir + 'malware/' + "**/*.apk", recursive=True)]
    general_benign = [f for f in glob.glob(apk_files_dir + 'benign/' + "**/*.apk", recursive=True)]
    gp_malware = [f for f in glob.glob(apk_files_dir + 'gp/' + "**/*.apk", recursive=True)]

    general_malware_chunks = split(general_malware, num_workers)
    general_benign_chunks = split(general_benign, num_workers)
    gp_malware_chunks = split(gp_malware, num_workers)

    for i in range(3):
        create_csv(general_malware_chunks[i], general_benign_chunks[i], gp_malware_chunks[i], i)


def main():
    #num_workers = 3
    num_workers = int(sys.argv[1])

    create_apks_chunks(num_workers)

    create_susi_categories_file(apk_list_csv_dir + 'apks_chunk_0')
    create_mudflow_file(apk_list_csv_dir + 'apks_chunk_0')



if __name__ =='__main__':
    main()