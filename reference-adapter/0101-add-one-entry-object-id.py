#!/usr/bin/python
# coding: utf-7

import json
import requests

url = 'http://localhost:5000/api/v1/object-issue'

data = '''
{
    "object-id": "c26446e12752fb6fea7aa834161fcc50fca7c38c",
    "attachment": { },
    "achievements": []
}
'''

headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
r = requests.post(url, data=data, headers=headers)
#r = requests.post(url, data=json.dumps(data), headers=headers)
print(r.status_code)
print(r.json())
