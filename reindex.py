import subprocess
import os
import logging
import boto3
from datetime import datetime
from elasticsearch5 import Elasticsearch
import random
import threading
import time
import shlex
import json
import sys
import requests
#from threading import timer

def sendSlackMessage(message):
    url = "<Webhook_URL>"
    title = ("Notification")
    slack_data = {
        "username": "Management",
        "icon_emoji": ":satellite:",
        #"channel" : "#somerandomcahnnel",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)


def queue(some_list):
    thread_list = []
    for index_name in some_list:
        thread = threading.Thread(target=reindex, args=(index_name,))
        thread_list.append(thread)
        if len(thread_list) >= 3:
            for proc in thread_list:
                proc.start()
            for proc in thread_list:
                proc.join()
            lecho("Starting new 3 threads")
            thread_list = []


def find_elasticsearch_node(region, node_generic_name):
    ec2 = boto3.resource('ec2', region_name=region)
    list_of_es_instances = []
    for i in ec2.instances.all():
        if i.tags:
            for tag in (i.tags):
                if tag['Key'] == 'Name':
                    instancename = tag['Value']
                    if str(instancename).startswith(node_generic_name):
                        list_of_es_instances.append(str(i.public_ip_address))
    return random.choice(list_of_es_instances)

current_pid = os.getpid()
log_location = "/tmp/" + str(current_pid) + ".log"
logging.basicConfig(
    filename=log_location,
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''): # b'\n'-separated lines
        lecho(f"got line from subprocess: {line}")

def lecho(line):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string + " " + line)
    logging.info(line)

def execute_command(command):
    execute = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if execute.returncode != 0:
        lecho("Error " + str(execute.stdout))
        exit()


def run_parallel_cmds(index_name): # currently not active
    timeout_sec = 480
    reindex_cmd = "php /home/ec2-user/trx_mon/dev/app/console trx:elastic:reindex --index {}".format(index_name)
    lecho(f"Subprocess {reindex_cmd}")
    proc = subprocess.Popen(shlex.split(reindex_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    timer = Timer(timeout_sec, proc.kill)
    try:
  #      timer.start()
        stdoutdata, stderrdata = proc.communicate()
        with proc.stdout:
            log_subprocess_output(proc.stdout)
    finally:
        lecho(f"Killing {reindex_cmd}")
 #       timer.cancel()
    if proc.returncode != 0:
        lecho(f"Failed: {reindex_cmd}")
        lecho(str(stdoutdata))
        lecho(f"Adding to list_of_failed_indexes")
        list_of_failed_indexes.append(index_name)
        index_to_delete = index_name + "_tmp"
        if es.indices.exists(index=index_to_delete):
            lecho(f"removing index {index_to_delete}")
            es.indices.delete(index=index_to_delete, ignore=[400, 404])
        else:
            lecho(f"Index {index_to_delete} does not exist")
    else: # if proc.returncode == 0
        if index_name in list_of_failed_indexes:
            list_of_failed_indexes.remove(index_name)

def reindex(index_name):
    tmp_index = f'{index_name}_tmp'
    es.indices.refresh()
    lecho(f"Searching for {tmp_index}")
    try:
        es.indices.delete(index=tmp_index)
    except:
        lecho(f"{tmp_index} does not exist")

    try:
        lecho(f"Trying reindex {index_name} to ${tmp_index}")
        result = es.reindex({"source": {"index": index_name}, "dest": {"index": tmp_index}}, wait_for_completion=True,
                        request_timeout=800)
    except:
        lecho(f"reindex to {index_name} has failed")
        lecho(f"Adding to list_of_failed_indexes")
        list_of_failed_indexes.append(index_name)
    else:
        if result['total'] and result['took'] and not result['timed_out']:
            lecho(f"Reindex completed from {index_name} to {tmp_index}")

        es.indices.refresh()
        try:
            if es.indices.exists(tmp_index):
                lecho(f"Deleting original index {index_name}")
                es.indices.delete(index=index_name)
            else:
                lecho(f"Cant delete orignal index {index_name} because {tmp_index} doesn;t exist")
                sys.exit()
        except:
            lecho(f"Error deleting {index_name}")
        else:
            lecho(f"Original index {index_name} deleted")

        es.indices.refresh()
        try:
            lecho(f"Reindexing from {tmp_index} back to {index_name}")
            result_to_og = es.reindex({"source": {"index": tmp_index}, "dest": {"index": index_name}}, wait_for_completion=True,  request_timeout=800)
        except:
            lecho(f"Error cant reindex {tmp_index} to ${index_name}")
        else:
            if result_to_og['total'] and result_to_og['took'] and not result_to_og['timed_out']:
                    lecho(f"Reindex to {index_name} completed")

        if index_name in list_of_failed_indexes:
            list_of_failed_indexes.remove(index_name)
    finally:
        if es.indices.exists(index=tmp_index) and es.indices.exists(index=index_name):
            lecho(f"removing index {tmp_index}")
            try:
                es.indices.delete(index=tmp_index, ignore=[400, 404])
                lecho(f"index {tmp_index} delete successfully")
            except:
                lecho(f"Error: cant delete index {tmp_index}")
                list_of_undeleted_indexes.append(tmp_index)
        elif es.indices.exists(index=tmp_index) and not es.indices.exists(index=index_name):
            lecho(f"Error cant delete {tmp_index} because {index_name} doesn't exist ")
        else:
            lecho(f"Index {tmp_index} does not exist")
            sys.exit()


region = "eu-west-1"
instance_names_start_with = "ES 56 Data"

es_server_ip = find_elasticsearch_node(region,instance_names_start_with)
lecho(f"Log location is at {log_location}")
lecho(f"Connecting to node {es_server_ip}")
es = Elasticsearch(
    [es_server_ip],
    scheme="http",
    port=9200,
)
if not es.ping():
    print(f"Error: connection failed to node {es_server_ip}")
    exit()

list_of_undeleted_indexes = []
list_of_failed_indexes = []
check_elastic_indices_cmd = "php /home/ec2-user/trx_mon/dev/jobs/check_elastic_indices.php > reindex.txt"
lecho(check_elastic_indices_cmd)
execute_command(check_elastic_indices_cmd)
list_of_bugged_indexes = []
with open("reindex.txt", 'r') as file:
    lines = file.readlines()
    lines = iter(lines)
    for line in lines:
        if line.startswith("Checking template"):
            index_name = line.split(":")[1]
            next_line = next(lines)
            if next_line.startswith("Missing fields"):
                list_of_bugged_indexes.append(index_name.rstrip().lstrip())


lecho(f"Running reindex on {list_of_bugged_indexes}")
queue(list_of_bugged_indexes)
if len(list_of_failed_indexes) is not 0:
    lecho(f"Running reindex on failed indexes{list_of_failed_indexes}")
    queue(list_of_failed_indexes)
else:
    lecho("No Failed indexes")
    lecho("Script finished")
    exit()

if len(list_of_failed_indexes) is not 0:
    lecho(f"failed indexes {list_of_failed_indexes}")
    lecho("Writing failed indexes to file")
    date_str = time.strftime("%Y%m%d")
    filename = f"failed_indexes-{date_str}.txt"
    lecho(f"list of undeleted indexes {list_of_undeleted_indexes}")
    lecho(f"file name is {filename}")

    with open(filename, 'w') as f:
        for index in list_of_failed_indexes:
            f.write(f"\n{index}")
else:
    lecho("No failed indexes left")
    lecho("Script has finished")
