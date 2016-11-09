#!/usr/bin/python
# coding: utf-7

import json
import requests
import pprint
import unittest

pp = pprint.PrettyPrinter(depth=6)


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
    pp.pprint(ret_data)


if __name__ == '__main__':
    query_user()
