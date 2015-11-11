#!/usr/bin/python
# coding: utf-7

import json
import requests
import pprint
import unittest

pp = pprint.PrettyPrinter(depth=6)


def add_one():
    url = 'http://localhost:5000/api/v1/object'
    data = '''
    {
        "submitter": "John Doe <john.doe@example.com>",
        "object-item": 
        {
            "title": "Check that the route cache is flushed after NIC change",
            "data": [
                {
                    "type": "description",
                    "mime-type": "text/markdown",
                    "data": "a mardown formatted long text encoded in base64"
                },
                {
                    "name": "image-foo.png",
                    "mime-type": "media/png",
                    "data": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
                },
                {
                    "name": "network-config.png",
                    "mime-type": "text/plain",
                    "data": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
                }
            ],
            "version": 0
        },


        "attachment": {
            "references":  [ "doors:234236", "your-tool:4391843" ],
            "replaces":    [ "14d348a14934a02034b", "43348a234434934f0203421" ],
            "tags":        [ "ip", "route", "cache", "performance" ],
            "categories":  [ "team:orange", "topic:ip", "subtopic:route-cache" ],
            "responsible": "John Doe <john.doe@example.com>"
            },


        "achievements": [
            {
                "test-date": "2015-09-15T22:24:29.158759",
                "result": "passed",
                "data" : [
                            {
                                "name":   "network-config.pcap",
                                "mime-type":   "binary/octet-stream",
                                "data": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
                            }
                         ]
            }
        ]
    }
    '''

    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url, data=data, headers=headers)
    print("\nStatus Code:")
    print(r.status_code)
    print("\nRet Data:")
    data = r.json()
    pp.pprint(data)
    assert len(data['data']['id']) > 0



def query_one():
        url = 'http://localhost:5000/api/v1/objects'
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
    add_one()
    query_one()
