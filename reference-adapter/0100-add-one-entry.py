#!/usr/bin/python
# coding: utf-7

import json
import requests

url = 'http://localhost:5000/api/v1/object-issue'

data = '''
{
    "object": 
    {
        "title": "Check that the route cache is flushed after NIC change",
        "categories": [
            "team:orange",
            "topic:ip",
            "subtopic:route-cache"
        ],
        "description": [
            {
                "type": "main",
                "mime-type": "text/markdown",
                "data": "a mardown formatted long text encoded in base64"
            },
            {
                "type": "media",
                "mime-type": "media/png",
                "description": "image of the routing architecture and test setup",
                "name": "image-foo.png",
                "data": "<base64 encoded image>"
            }
        ],
        "version": 0,
        "data": [
            {
                "description": "network configuration script",
                "file-name": "network-config.sh",
                "mime-type": "text/plain",
                "data": "<base64 encoded data>"
            }
        ]
    },
    "attachment": {
        "references": [ "doors:234236", "your-tool:4391843" ],
        "replaces":   [ "14d348a14934a02034b", "43348a234434934f0203421" ],
        "tags":       [ "ip", "route", "cache", "performance" ]
        },
    "achievements": [
        {
            "submitter": "John Doe <john.doe@example.com>",
            "test-date": "2015-09-15T22:24:29.158759",
            "result": "passed",
            "sender-id": "virgo.skynet.local",
            "data" : [
                        {
                            "description": "foo-bar pcap file",
                            "file-name":   "network-config.sh",
                            "mime-type":   "binary/octet-stream",
                            "data":        "<base64 encoded data>"
                        }
                     ]
        }
    ]
}
'''

headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
r = requests.post(url, data=data, headers=headers)
#r = requests.post(url, data=json.dumps(data), headers=headers)
print(r.status_code)
print(r.json())
