#!/usr/bin/python
# coding: utf-7

import json
import requests
import pprint
import unittest

pp = pprint.PrettyPrinter(depth=6)


def add_n(n):
    url = 'http://localhost:5000/api/v1/object'
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
        pp.pprint(data)
        dj = json.dumps(data, sort_keys=True, separators=(',', ': '))
        r = requests.post(url, data=dj, headers=headers)
        print("\nStatus Code:")
        print(r.status_code)
        print("\nRet Data:")
        ret_data = r.json()
        pp.pprint(ret_data)
        assert len(ret_data['data']['id']) > 0



    url = 'http://localhost:5000/api/v1/object'
    data = '''
    {
        "limit": 1000,
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
    add_n(10)
