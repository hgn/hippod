#!/usr/bin/python3
# coding: utf-8

import sys
import json
import requests
import pprint
import unittest
import string
import random
import os
import json
import time
import datetime
import base64
import uuid
import argparse
import string

pp = pprint.PrettyPrinter(depth=6)

parser = argparse.ArgumentParser()
parser.add_argument('--quite',
                    help='Just print an OK at the end and fade out the printed data',
                    action='store_true')
args = parser.parse_args()

def pprnt(data):
    if args.quite:
        pass
    else:
        pp.pprint(data)


def random_image():
    scrip_path = os.path.dirname(os.path.realpath(__file__))
    image_path = os.path.join(scrip_path, 'data', 'plot.png')
    with open(image_path, "rb") as f:
        content = f.read()
        return base64.b64encode(content)

def random_id():
    return str(uuid.uuid4())[0:5]

def random_title(words):
    words = ['Foo', 'Bar']
    s = ' '.join(random.choice(words) for _ in range(1))
    return s

def random_result():
    d = ['passed', 'failed', 'nonapplicable' ]
    return d[random.randint(0, len(d) - 1)]

def random_submitter():
    d = ['albi', 'isac43', 'tesla_driver', 'maryy', 'charlie']
    return d[random.randint(0, len(d) - 1)]

def query_full(id, sub_id):
    url = 'http://localhost:8080/api/v1/object/{}/{}'.format(id, sub_id)
    data = ''' '''
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(url, data=data, headers=headers)
    print("\nStatus Code:")
    print(r.status_code)
    print("\nRet Data:")
    data = r.json()
    pprnt(data)

def add_n(n):
    url = 'http://localhost:8080/api/v1/object'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    for i in range(n):
        data = dict()
        data["submitter"] = random_submitter()
        data["object-item"] = dict()
        data["object-item"]['categories'] = [ "team:orange", "topic:ip", "subtopic:route-cache" ]
        data["object-item"]['version'] = random.randint(0,1)
        data['object-item']['title'] = "{}".format(random_title(3))

        data['object-item']['data'] = list()
        desc_data = dict()
        desc_data['type'] = 'description'
        desc_data['mime-type'] = 'text/markdown'
        # base64 requires a byte array for encoding -> .encode('utf-8')
        # json requires a string -> convert to UTF-8
        default_string = (
                """
# Rooter: A Methodology for the Typical Unification of Access Points and Redundancy #

Collaboratively administrate empowered **markets** via plug-and-play networks.
Dynamically procrastinate __B2C users__ after installed base benefits. Dramatically
visualize customer directed convergence without **revolutionary ROI**.

    int foo(void) {
        abort(0);
    }

* Item1
* Item2
* Item3

Proctively envisioned multimedia based expertise and cross-media growth
strategies. Seamlessly visualize quality intellectual capital without superior
collaboration and idea-sharing. Holistically pontificate installed base portals
after maintainable products.

![Description](image.png)


## Harnessing Byzantine Fault Tolerance Using Classical Theory ##

Efficiently unleash cross-media information without cross-media value. Quickly
maximize **timely deliverables** for real-time schemas. Dramatically maintain
clicks-and-mortar __solutions__ without functional solutions.


Completely synergize resource taxing relationships via premier niche markets.
Professionally cultivate one-to-one customer service with robust ideas.
Dynamically innovate resource-leveling customer service for state of the art
customer service.

    +---------+
    |         |                        +--------------+
    |   NFS   |--+                     |              |
    |         |  |                 +-->|   CacheFS    |
    +---------+  |   +----------+  |   |  /dev/hda5   |
                 |   |          |  |   +--------------+
    +---------+  +-->|          |  |
    |         |      |          |--+
    |   AFS   |----->| FS-Cache |
    |         |      |          |--+
    +---------+  +-->|          |  |
                 |   |          |  |   +--------------+
    +---------+  |   +----------+  |   |              |
    |         |  |                 +-->|  CacheFiles  |
    |  ISOFS  |--+                     |  /var/cache  |
    |         |                        +--------------+
    +---------+

Proctively envisioned multimedia based expertise and cross-media growth
strategies. Seamlessly visualize quality intellectual capital without superior
collaboration and idea-sharing. Holistically pontificate installed base portals
after maintainable products.

## Shizzle Dizzle Header Second Order ##

Proctively envisioned multimedia based expertise and cross-media growth
strategies. Seamlessly visualize quality intellectual capital without superior
collaboration and idea-sharing. Holistically pontificate installed base portals
after maintainable products.

                """)
        changing_string = random.choice(['A','B','C']) + random.choice(['A','B','C'])
        string_final = default_string + changing_string 
        desc_data['data'] = base64.b64encode(string_final.encode('utf-8')).decode("utf-8") 
        data['object-item']['data'].append(desc_data)

        img_data = dict()
        img_data['name'] = 'image.png'
        img_data['mime-type'] = 'image/png'
        img_data['data'] = random_image().decode("utf-8") 
        data['object-item']['data'].append(img_data)

        img_data = dict()
        img_data['name'] = 'trace.pcap'
        img_data['mime-type'] = 'application/vnd.tcpdump.pcap'
        img_data['data'] = "R0lGODlhDwAPAKECAAAAzxzM/////wAAACwAAAAADwAPAAACIISPeQHsrZ5ModrLlN48CXF8m2iQ3YmmKqVlRtW4MLwWACH+H09wdGltaXplZCBieSBVbGVhZCBTbWFydFNhdmVyIQAAOw=="
        data['object-item']['data'].append(img_data)

        data["attachment"] = dict()
        data["attachment"]['references'] = [ "doors:234236", "your-tool:4391843" ]
        data["attachment"]['tags'] = [ "ip", "route", "cache", "performance" ]
        data["attachment"]['categories'] = [ "team:orange", "topic:ip", "subtopic:route-cache" ]
        data["attachment"]['responsible'] = data["submitter"]

        achievement = dict()
        achievement["test-date"] = datetime.datetime.now().isoformat('T')
        achievement["result"] = random_result()

        # 1/4 of all achievements are anchored
        if random.randint(0, 3) == 0:
            achievement["anchor"] = random_id()

        # add data entry to achievement, can be everything
        # starting from images, over log files to pcap files, ...
        achievement['data'] = list()
        log_data = dict()
        log_data['name'] = 'result-trace.pcap'
        log_data['mime-type'] = 'application/vnd.tcpdump.pcap'
        log_data['data'] = "R0lGODlhDwAPAKECAAABzMzM/////wAAACwAAAAADwAPAAACIISPeQHsrZ5ModrLlN48CXF8m2iQ3YmmKqVlRtW4MLwWACH+H09wdGltaXplZCBieSBVbGVhZCBTbWFydFNhdmVyIQAAOw=="
        achievement['data'].append(log_data)

        if random.randint(0, 3) == 0:
            variety = dict()
            variety['os-version'] = 'rhel23'
            variety['platform']   = 'xeon-foo'
            achievement["variety"] = variety

        data["achievements"] = list()
        data["achievements"].append(achievement)

        #os.system('cls' if os.name == 'nt' else 'clear')
        print("New Data:\n-----------\n")
        print(json.dumps(data, sort_keys=True, separators=(',', ': '), indent=4))
        print("\n-----------\n")

        dj = json.dumps(data, sort_keys=True, separators=(',', ': '))
        r = requests.post(url, data=dj, headers=headers)
        print("Return Data:\n-----------\n")
        ret_data = r.json()
        print(json.dumps(ret_data, sort_keys=True, separators=(',', ': '), indent=4))
        assert len(ret_data['data']['id']) > 0
        processing_time = ret_data['processing-time']
        sys.stderr.write("\nHTTPStatusCode: {} ServerProcTime {}s\n".format(r.status_code, processing_time))

        query_full(ret_data['data']['id'], ret_data['data']['sub_id'])
        time.sleep(1)

    print("\r\n\n")
    sys.exit(0)
    print("\r\n\n")

    url = 'http://localhost:8080/api/v1/objects'
    data = '''
    {
        "limit": 0,
        "ordering": "by-submitting-date-reverse",
        "maturity-level": "all"
    }
    '''

    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(url, data=data, headers=headers)
    print("\nStatus Code:")
    print(r.status_code)
    print("\nRet Data:")
    data = r.json()
    pprnt(data)
    return r.status_code


if __name__ == '__main__':
    status = add_n(10000)
    if status==200:
        print("OK")
    else:
        print("FAIL")
