#!/usr/bin/python
# coding: utf-7

import json
import requests
import pprint
import unittest
import argparse

pp = pprint.PrettyPrinter(depth=6)

arser = argparse.ArgumentParser()
parser.add_argument('--quite', help='Just print an OK at the end and fade out the printed data' )
args = parser.parse_args()

def pprnt(data):
    if args.quite:
        pass
    else:
        pp.pprint(data)


def query_user():
    url = 'http://localhost:8080/api/v1/users'
    data = dict()
    data["filter"] = dict() 
    data["filter"]['username'] = 'john_doe'

    dj = json.dumps(data, sort_keys=True, separators=(',', ': '))
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url, data=dj, headers=headers)
    print("\nStatus Code:")
    print(r.status_code)
    print("\nRet Data:")
    ret_data = r.json()
    pprnt(ret_data)


if __name__ == '__main__':
    query_user()
