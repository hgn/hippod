#!/usr/bin/python
# coding: utf-7

import json
import requests

url = 'http://localhost:5000/api/v1/object-issue'

data = '''
{
    "title": "Check that the route cache is flushed after NIC change",
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
    "categories": [
        "team:orange",
        "topic:ip",
        "subtopic:route-cache"
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
}
'''

headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
r = requests.post(url, data=data, headers=headers)
#r = requests.post(url, data=json.dumps(data), headers=headers)
print(r.status_code)
print(r.json())
