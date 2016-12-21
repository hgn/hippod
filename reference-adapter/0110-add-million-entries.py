#!/usr/bin/python3
# coding: utf-8

import sys
import json
import requests
import pprint
import unittest
import string
import random
import argparse

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


def random_title(length):
    words = ['Foo', 'Bar', 'Linux', 'Something', 'Yeah', 'Nope', 'Random', "REST", "IPv6"]
    s = ' '.join(random.choice(words) for _ in range(5))
    return s

def add_n(n):
    url = 'http://localhost:8080/api/v1/object'
    data = dict()
    data["submitter"] = "john_doe"
    data["object-item"] = dict()
    data["object-item"]['categories'] = [ "team:orange", "topic:ip", "subtopic:route-cache" ]
    data["object-item"]['version'] = 0
    #data["attachment"] = dict()
    data["achievements"] = list()

    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    for i in range(n):
        data['object-item']['title'] = "{}".format(random_title(80))
        #pp.pprint(data)
        dj = json.dumps(data, sort_keys=True, separators=(',', ': '))
        r = requests.post(url, data=dj, headers=headers)
        #print("\nStatus Code:")
        #print(r.status_code)
        #print("\nRet Data:")
        ret_data = r.json()
        #pp.pprint(ret_data)
        assert len(ret_data['data']['id']) > 0
        processing_time = ret_data['processing-time']
        if args.quite:
            pass
        else:
            sys.stderr.write("\rEntry: {}, HTTPStatusCode: {} ServerProcTime {}s".format(i, r.status_code, processing_time))

    pprnt("\r\n\n")

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
    pprnt("\nStatus Code:")
    pprnt(r.status_code)
    pprnt("\nRet Data:")
    data = r.json()
    pprnt(data)
    return r.status_code

if __name__ == '__main__':
    status = add_n(2000)
    if status==200:
        print("OK")
    else:
        print("FAIL")
