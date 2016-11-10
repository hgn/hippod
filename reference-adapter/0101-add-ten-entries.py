#!/usr/bin/python3
# coding: utf-8

import json
import requests
import pprint
import unittest
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



def add_n(n):
    url = 'http://localhost:8080/api/v1/object'
    data = dict()
    data["submitter"] = "John Doe <john.doe@example.com>"
    data["object-item"] = dict()
    data["object-item"]['title'] = "Foo Bar Title"
    data["object-item"]['categories'] = [ "team:orange", "topic:ip", "subtopic:route-cache" ]
    data["object-item"]['version'] = 0
    data["attachment"] = dict()
    data["achievements"] = list()

    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    for i in range(n):
        data['object-item']['title'] = "title {}".format(i)
        pprnt(data)
        dj = json.dumps(data, sort_keys=True, separators=(',', ': '))
        r = requests.post(url, data=dj, headers=headers)
        pprnt("\nStatus Code:")
        pprnt(r.status_code)
        pprnt("\nRet Data:")
        ret_data = r.json()
        pprnt(ret_data)
        assert len(ret_data['data']['id']) > 0



    url = 'http://localhost:8080/api/v1/objects'
    data = '''
    {
        "limit": 1000,
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
    status = add_n(10)
    if status==200:
        print("OK")
    else:
        print("FAIL")