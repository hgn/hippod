#!/usr/bin/python
# coding: utf-7

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

pp = pprint.PrettyPrinter(depth=6)

def random_title(words):
    words = ['Foo', 'Bar', 'Linux', 'Something', 'Yeah', 'Nope', 'Random', "REST", "IPv6"]
    s = ' '.join(random.choice(words) for _ in range(11))
    return s

def random_result():
    return ['passed', 'failed'][random.randint(0,1)]

def random_submitter():
    d = ['Albert Einstein', 'Isaac Newton', 'Nikola Tesla', 'Marie Curie', 'Charles Darwin']
    return d[random.randint(0, len(d) - 1)]

def add_n(n):
    url = 'http://localhost:5000/api/v1/object'
    data = dict()
    data["submitter"] = random_submitter()
    data["object-item"] = dict()
    data["object-item"]['categories'] = [ "team:orange", "topic:ip", "subtopic:route-cache" ]
    data["object-item"]['version'] = 0
    data["attachment"] = dict()
    data["achievements"] = list()

    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    for i in range(n):
        data['object-item']['title'] = "{}".format(random_title(80))
        os.system('cls' if os.name == 'nt' else 'clear')
        print("New Data:\n-----------\n")
        print(json.dumps(data, sort_keys=True, separators=(',', ': '), indent=4))
        print("\n-----------\n")
        print("Submit Data in 5 Seconds ...\n")
        time.sleep(5)
        dj = json.dumps(data, sort_keys=True, separators=(',', ': '))
        r = requests.post(url, data=dj, headers=headers)
        #print("\nStatus Code:")
        #print(r.status_code)
        #print("\nRet Data:")
        ret_data = r.json()
        #pp.pprint(ret_data)
        assert len(ret_data['data']['id']) > 0
        processing_time = ret_data['processing-time']
        sys.stderr.write("\rEntry: {}, HTTPStatusCode: {} ServerProcTime {}s".format(i, r.status_code, processing_time))

    print("\r\n\n")

    url = 'http://localhost:5000/api/v1/objects'
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
    pp.pprint(data)


if __name__ == '__main__':
    add_n(1)
