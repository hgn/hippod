
# Hippod - Problem Statement

Larger software projects often utilizes many different test systems. Each test
system/product comes with it own reporting tool making it difficult to get an
unified view across this heterogeneous landscape for specific software
versions. Hippod is a generic framework to unify the view in one common
application.

![alt text](images/hippod-test-system-interaction.png "Architecture")

# Features

- **Simplicity**, number one design decision was that interaction with hippod are
	nearly invisible. You even need no unique test number, a title & category are
	enough.
- **Traceability**, unlike any known test system Hippod identify tests based on
	the content, not on "unique numbers". If a test change, e.g. a variable in
	the test change, hippod detects this. If a test is stored in hippod you will
	exactly know what the test was including the exact test environment and used
	source code. See more in the Traceability section.
- **Manageable**, manage test databases is cumbersome. Outdated & invalid tests
	still in the database requires human ressourcs. Hippod inculded gardbage
	mechanism try to remove outdated entries automatically.
- **Scalability**, larger test systems can contain thousands of tests. Hippod
	was designed with this requirement in mind. Where possible the complexity of
	algorithms was designed to be O(1) - so running in constant time no matter
	how many entries are in the database.
- **Powerful export capabilities**, the integrated web-gui is the management
	console to see the status of all tests. Sort them, limit, filter for teams or
	tags, etc. To provide reports hippod can export to several formats like PDF
	or even ePUB.

# Traceability


# Integration Into Existing Test Inrastructure

Hippod speaks REST - so you can use your programming language of choice to feed
Hippod with test data and results. If your test system is written in Python/Swift/Go
with build-in HTTP/JSON support it is a trivial to connect your testsystem and
Hippod. If you use plain C you probably want to use one of our existing Python
based adapter.

A minimal example including title, description, category, tags and result is
illustrated in the next lines (be aware: normally you will hide these details
in a separate library so that you have even fewer hippod specific code):

```
import json
import requests

hippo_url = 'http://localhost:8080/api/v1/object'
test_data = """
{
  "submitter" : "john_doe",
  "object-item" " {
    "title" : "This is my first test",
    "categories" : [ "team:orange", "topic:ip", "subtopic:route-cache" ],
    "tags" : [ "ip", "route", "network" ],
  }
  "achievements" : [
    { 'result' : 'passed', 'test-date' : '2016-01-01' }
  ]
}
"""
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
r = requests.post(hippo_url, data=test_data, headers=headers)
print("Result {}".format(r.json()))
```

# What is a Test?


# Installation

Hippod is written in Python3 using asyncio/aiohttp. To generate PDF reports
pandoc/xetex is required. For LDAP functionality libldap is required. Hippod
is tested on Debian/Ubuntu and Arch Linux. For Debian based systems the following
three lines should install all required dependencies:

```
sudo apt-get install python3-pip libsasl2-dev pandoc texlive-xetex
sudo apt-get install texlive-latex-extra texlive-latex-recommended libldap-dev
sudo pip3 install -r requirements.txt
```

To install hippod the next lines should do the trick:

```
# clone and install runtime files
git clone https://github.com/hgn/hippod.git
cd hippod
sudo make install

# edit configuration for LDAP support, if not defaults are fine
vim /etc/hippod/hippod-configuration.json

# start and enable hippod with systemd
sudo systemctl daemon-reload
sudo systemctl start hippod
sudo systemctl enable hippod

# follow logfile
sudo journalctl -f -u hippod
```

Point you webbrowser to localhost:8080 - that's all.

# Licence

Simple MIT licensed. Install where you want and how often you want. If you make
a product out of Hippod - great! The only request is that the LICENSE file must
be intact, that's all.

# Privacy Statement

Hippod will never query external resources like Java Script libraries or Google
Fonts. All resources are stored within hippod. This was one major design
decision: never leak data to third party sides. Hippod can be operated behind
cooperate firewalls/proxies.
