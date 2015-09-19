#!/usr/bin/python
# coding: utf-7

import json
import requests

url = 'http://localhost:5000/api/v1/object'

data = '''
{
    "object-item": 
    {
        "title": "Check that the route cache is flushed after NIC change",
        "data": [
            {
                "type": "main",
                "mime-type": "text/markdown",
                "data": "a mardown formatted long text encoded in base64"
            },
            {
                "description": "image of the routing architecture and test setup",
                "file-name": "image-foo.png",
                "mime-type": "media/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
            },
            {
                "description": "network configuration script",
                "file-name": "network-config.sh",
                "mime-type": "text/plain",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
            }
        ],
        "categories": [
            "team:orange",
            "topic:ip",
            "subtopic:route-cache"
        ],
        "version": 0
    },


    "attachment": {
        "references":  [ "doors:234236", "your-tool:4391843" ],
        "replaces":    [ "14d348a14934a02034b", "43348a234434934f0203421" ],
        "tags":        [ "ip", "route", "cache", "performance" ],
        "responsible": "John Doe <john.doe@example.com>"
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
                            "data": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
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
