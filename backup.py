#!/usr/bin/env python3

import os
import shutil
import requests
import json
import filecmp
from datetime import datetime
from time import sleep

# SETTINGS BEGIN
settings = {}
settings["API_URL"] = "https://api.gandi.net/v5"
settings["API_KEY"] = None
settings["DATA_PATH"] = "/data"
settings["TMP_PATH"] = "/tmp/data"
settings["INTERVAL"] = 24 # in hours (0 for one shot)
# SETTINGS END

BACKUPED_RESOURCES = [
    'domain/domains/{domain}',
    'domain/domains/{domain}/nameservers',
    'domain/domains/{domain}/livedns',
    'livedns/domains/{domain}/keys',
    'livedns/domains/{domain}/records',
    'livedns/domains/{domain}/snapshots',
    'email/forwards/{domain}',
    'email/mailboxes/{domain}'
]

for setting in settings:
    # Take environment settings if defined
    if setting in os.environ:
        settings[setting] = os.environ[setting]

HEADERS = {'Authorization': 'Apikey %s' % settings["API_KEY"]}

def write_log(msg):
    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S")+' : '+msg)

def prepare_tmp_directory():
    if os.path.exists(settings["TMP_PATH"]):
        shutil.rmtree(settings["TMP_PATH"])
    os.makedirs(settings["TMP_PATH"])

def compare(comparison):
    if comparison.diff_files:
        return False
    for sub_comparison in comparison.subdirs.values():
        if not compare(sub_comparison):
            return False
    return True

def compare_folders(folder_a, folder_b):
    if os.path.exists(folder_a) and os.path.exists(folder_b):
        return compare(filecmp.dircmp(folder_a, folder_b))
    else:
        return False

def get(resource):
    try:
        response = requests.get(settings["API_URL"]+'/'+resource+'?per_page=500', headers=HEADERS)
        data = json.loads(response.text)
        for element in data:
            if "quota_used" in element:
                element.pop("quota_used")
        return data
    except:
        print("Error :"+response.text)
        return None

def save_resource(resource):
    write_log(resource)
    data = get(resource)
    path = resource.split('/')
    directory_path = settings["TMP_PATH"]+'/'+'/'.join(path[:-1])
    file_name = path[-1]+'.json'
    full_path = directory_path+'/'+file_name
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    with open(full_path, 'w') as json_file:
        json.dump(data, json_file, indent=2, sort_keys=True)

def get_domains_list():
    domains_list = get('domain/domains')
    domains = []
    for domain in domains_list:
        domains.append(domain["fqdn"])
    return domains

def backup_domain_resources(domain):
    for resource_to_backup in BACKUPED_RESOURCES:
        resource = resource_to_backup.replace('{domain}', domain)
        save_resource(resource)

def backup_domains(domains_list):
    for domain in domains_list:
        backup_domain_resources(domain)

def backup_all():
    domains = get_domains_list()
    save_resource('domain/domains')
    backup_domains(domains)

def store_backup():
    if os.path.exists(settings["DATA_PATH"]+'/current'):
        os.unlink(settings["DATA_PATH"]+'/current')
    now = datetime.now().strftime("%Y/%m/%d/%H-%M-%S")
    shutil.copytree(settings["TMP_PATH"], settings["DATA_PATH"]+'/'+now)
    os.symlink('./'+now, settings["DATA_PATH"]+'/current')

if __name__ == "__main__":
    while int(settings["INTERVAL"]) > 0:
        prepare_tmp_directory()
        backup_all()
        print('Backup success')
        if not compare_folders(settings["TMP_PATH"], settings["DATA_PATH"]+'/current'):
            store_backup()
            write_log('New version stored')
        else:
            write_log('Nothing changed')
        print('Sleeping for {}h'.format(str(settings["INTERVAL"])))
        sleep(int(settings["INTERVAL"]) * 60 * 60)

