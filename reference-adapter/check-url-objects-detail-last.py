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
    url = 'http://localhost:8080/api/v1/objects-detail-last'
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
    status = add_n(1)
    if status==200:
        print("OK")
    else:
        print("FAIL")