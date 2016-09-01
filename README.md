
# Introduction #

![alt tag](https://raw.githubusercontent.com/hgn/hippod/master/doc/process.png)


## Installation and Dependencies ##

Only python and python-flask is required to run contestcolld.

### Microsoft Windows ###

Since Python version 2.7.9 *pip* is already included in standard python. A
simple ```pip install flask``` will then install flask.

There are several ways to install *pip* by hand but I recommend using a actual
Python version.

### Linux ###

#### Debian and Ubuntu ####

```
sudo apt-get install python-flask
sudo apt-get install python3-markdown
```

#### Arch ####

```
sudo pacman -S community/python2-flask
```

### Testing Dependencies ###

Python request package is required for build in tests. You can use:

```
sudo pacman -S python2-requests-toolbelt-0.4.0-1
```

## Starting contestcolld #

Simple start the ```run.py``` script in the main directory for simple output.
To use this package in a productive environment you can use *nginx* to power up
flask. Search for *nginx* and *flask* how to setup nginx correctly.

## Backup Production Data - Database ##

All information is stored in plain txt files in the configured database path. A
tarball and a previous temporary shutdown of the server (to eliminate
inconsistency) is suficiently to backup all data.


# Developer Information #

## Color Guidelines ##

If colors are required for webdesign only a few should be taken. Each color
**must** be taken from the Google Material Design scheme.

If random colors are required, e.g. for users, then these colors should be
monochromatic.

A java script tool to generate monochromatic colors is
[please](http://www.checkman.io/please/)

## Coding Guidelines ##

* Python PEP8
* Lines not longer then 90 characters (exceptions possible)
* Function length not longer then screen height

## Directory Structure ##

http://www.plankandwhittle.com/packaging-a-flask-web-app/

# Concept and Architecture #

This document describes the internal and external API of contestcolld.
Understanding this document provides nearly all required information how
contestcolld works internally, how contestcolld can be extended and what are
the basic concept behind contestcolld.

![alt tag](https://raw.githubusercontent.com/hgn/contestcolld/master/doc/architecture.png)

## Exchange Object ##

Short xobject is the exchange format where all data is encapsulated. The xobj
**MUST** contain a object or a object-id - but not both. It **CAN** contain a
attachment dictionary and **CAN** contain a achievements list.

```
{
    "object-id": "c26446e12752fb6fea7aa834161fcc50fca7c38c",
    "attachment": { },
    "achievements": []
}
```

## Object ##

Is immutable once it is in the system. Has several required attributes. If a
attribute change or new attributes are added a new object is internally
generated. A object is unique identifyable by a ID. The id is a SHA256 of all
ORed key and value pairs of the object.

A *Object Issue* include two kind of attributes: required and optional
attributes. The difference is that requires attributes are required for the
base system to work with. They will be display, ordered etc. based on this
information. Optional attributes on the other hand are in the responsibility of
the user. They provide a way to extend contestcolld for special use-cases
without the risk of name clashes.

### Required attributes ###

* Title
* Description
* Categories
* Version
* Data

```
{
	"title" : "Check that the route cache is flushed after NIC change",
	"description": [
	  {
			"type": "main":
			"mime-type":   "text/markdown",
			"data": "a mardown formatted long text encoded in base64"
		},
	  {
			"type":        "media",
			"mime-type":   "media/png",
			"description": "image of the routing architecture and test setup",
			"name":        "image-foo.png",
			"data":        "<base64 encoded image>"
		},
	],
	"categories": [ "team:orange", "topic:ip", "subtopic:route-cache" ],
	"version":    0,
	"data" : [
	  {
			"description": "network configuration script"
			"file-name":   "network-config.sh"
			"mime-type":   "text/plain",
			"data":        "<base64 encoded data>"
		}
	]

	[ optional attributes ]
}
```

#### Title ####

The title should be short and concise. The title should be not longer then 100
characters. In the Web GUI the title is shorten if longer.

#### Description ####

Must be available but can be an empty list if no further description is
available or makes no sense. If a description is given then a *type* must be
given. This must be *main* or *media*. There **MUST** be exactly one main type
and 0 - ∞ media types.

Media types **MUST** have a mime type. Currently supported media types are:

* ```media/png```
* ```media/gif```
* ```media/jpeg```

The maximum size for media types is currently 500 kByte (base64 encoded, actual
image size is even smaller). Larger media types are currently not supported.

If several media types are given the name must be unique. No name clashes are
allowed.

The description is optional.

#### Categories ####

Categories are ordered in the list. A Object issue MUST specify at least one
categories but can specify more. Categories are the mechanism to group test to
teams or functional aspects. Categories are a powerfull and flexible mechanism
for grouping.

You can categorize on the first level on the project structure. The next level
can be the topic and next the subtopic. If a test was done as a unit-test or a
black-box test should rather be specified as a tag in the object attachment
attributes.

If you have no categories because the project is small you can use "common".

#### Version ####

Version start with 0 and can be an BigInt.

#### Data ####

data can be a empty list. If entry is provided then the description, file-name,
mime-type and the base64 encoded data must be provided.

### Tip ###


Sometimes it is required to obsolete one particular test. Then the version
can be incremented or on the other hand in the object attachments the replaces
attribute can be used.

### Optional User Attributes ###

Optional attributes are not standardized. You can add all possible kind of
optional attributes. The only limitation is that if new attributes added later
it will violate the *object issue* immutable guarantee and a new object is
created - exactly the same behavior as for *required attributes*.

Optional attributes *MUST* start with a underscore in the name to prevent
further name clashes.

```
{
	[ required attributes ]

	"_serial": 0,
	"_release": 666,
}
```

NOTE: user attributed must start with a underscore followed by a character with
the exception of another underscore. Keys starting with two underscore
(```__foo```) are reserved for internal data. E.g. to save additional data
without influence the common concept. So double underscore are special too.
Double underscore data are for example not checksummed.


## Object Attachments ##

Object attachments are strictly bound to a particular object - but in contrast
the object attachment attributes may change without resulting in a new object.

Attachments are optional. Attachments can be added at any time.

Object Attachments attributes are images, matlab files, explaining text etc.
pp.

If attachments are later changes (e.g. new attributes added) this will apply to
all already performed tests. 

```
{
	"references": [ "doors:234234", "your-tool:4391843" ],
	"replaces":   [ "14d348a14934a02034b", "43348a234434934f0203421" ],
	"tags":       [ "ip", "route", "cache", "performance" ],
}
```

Objects attachment updates a object, thus Attachment attributes can be removed
at any time.


## Object Achievement ##

Executed test and their results are collected as *Object Achievements*. They
can contain 

```
{
	"name": "John Doe",
	"date": "30230303",
	"result" : "passed | failed | nonapplicable",
	"sender-id" : "windows-workgroups-id",
	"data" : [
	  {
			"description": "foo-bar pcap file"
			"file-name":   "network-config.sh"
			"mime-type":   "binary/octet-stream",
			"data":        "<base64 encoded data>"
		}
	],

	"__date_added": "30230303"
}
```

### Required Attributes ###

* name
* date
* result

#### Date ####

The exact date when the test was done. This must be provided from the user
because a long running test may run over several days. The only way to get the
exact date is that the user provide it. Disadvantage is that the local clock
may not be synced.

To make things bullet proof the contestcolld will additionally store the date
when the entry was added: ```__date_added```. The WEB GUI to display
Achievements will use the internal format - just because it is bullet proof.
If the date between __date_added and date differs for more then one day a
warning is printed to the WEB GUI console.

### Optional Attributes

Optional attributes are evaluated if available. 

* sender-id
* data
* release

### User Specific Attributes

Must start with a underscore in their name.

## Object Container ##

Within the daemon the object is embedded into a object container. The object
container add metadata like when was the object first be added to the database
and who added the object and the calculated sha256 sum for faster indexing.

```
{
	"object-id": 8f348a14934f302034a
	"object" : <OBJECT>,
	"object-attachment" : <OBJECT>,
	"date-added": 12-21-2013,
	"object-achievements" = [
		{
			"id": 1,
			"date-uploaded": "date when stored in database, not user provided date",
		},
		{
			"id": 2,
			"date-uploaded": "date when stored in database, not user provided date",
		},
	]
}
```

The object-id is the SHA256 of the object-issue. But the object container can
only contain one particular object-issue. To identify a object-container
exactly the SHA256 of the object-issue is the ideal key.

Object achievement IDs are incremented at each new added achievement.


## Release Label ##

```
[
	{
		"id": 1,
		"description": "Tests for Release v4.1",
		"content": [
			{
			"object-id": "8f348a14934f302034a",
			"object-achievements-id": 2
			},
			{
			"object-id": "df348a14934f302034a",
			"object-achievements-id": 0
			},
		]
	},
	{
		"id": 2,
		"description": "Tests for Release v4.2",
		"content": [
			{
			"object-id": "8f348a14934f302034a",
			"object-achievements-id": 2
			},
		]
	},
	[...]
]
```

# SHA265 Calculation #

The calculation of the unique sha265 is done in the following manner:

* provide an emty string, called buf
* sort the dictornary using the keys
* iterate over the dictionary and add the value string to buf
* if value is a integer convert to string before
* if value is a string list: add each entry
* if value is again a dictionary enter the loop again
* at the end calculate the sha256 sum of the string - this is the ID.

It is important that the calculation of the ID is known and implemented equally
because client and server components will calculate their ID's on their own. Shifting
the calculation to the server component result in unwanted higher network traffic.

# Database File Layout #

```
db/objects/
db/release-labels.db
```

## Typical Layout after some entries ##

```
db/objects/35/358548239f0593/container.db
db/objects/35/358548239f0593/achievements/0.db
db/objects/35/358548239f0593/achievements/1.db
db/objects/35/358548239f0593/achievements/2.db
db/objects/f1/f1048a91949a32/container.db
db/objects/f1/f1048a91949a32/achievements/0.db
db/objects/f1/f1048a91949a32/achievements/1.db
db/objects/f1/f1b19d018a4801/container.db
db/objects/f1/f1b19d018a4801/achievements/0.db
db/objects/f1/f1b19d018a4801/achievements/1.db
db/objects/f1/f1b19d018a4801/achievements/2.db
db/objects/f1/f1b19d018a4801/achievements/3.db
db/objects/2a/2a58ab18348219/container.db
db/objects/2a/2a58ab18348219/achievements/0.db
db/objects/2a/2a58ab18348219/achievements/2.db
db/release-labels.db
```

## REST Query and Manipulation API ###

### Manipulation API ###

```
POST api/v1/object-issue
POST api/v1/object-attachment
POST api/v1/object-achievement

POST api/v1/release-label
```

### Query API ###

Media and data types like files are not returned. To return media types as well
the query string must explicetly enable this. This restriction is to reduce
overall bandwidth consumption.

```
GET api/v1/object-issues
GET api/v1/object-issues/id

GET api/v1/object-attachment/id
GET api/v1/object-achievement/id

GET api/v1/release-label
GET api/v1/release-label/id
```

# Project Structure #

```
.
├── contestcolld
│   ├── assets
│   │   ├── css
│   │   │   ├── bootstrap.min.css
│   │   │   └── styles.css
│   │   ├── fonts
│   │   │   ├── glyphicons-halflings-regular.eot
│   │   │   ├── glyphicons-halflings-regular.svg
│   │   │   ├── glyphicons-halflings-regular.ttf
│   │   │   ├── glyphicons-halflings-regular.woff
│   │   │   └── glyphicons-halflings-regular.woff2
│   │   └── js
│   │       ├── bootstrap.min.js
│   │       ├── jquery.min.js
│   │       └── scripts.js
│   ├── gui.py
│   ├── api.py
│   ├── db-backend-file.py
│   ├── __init__.py
│   └── templates
│       ├── footer.html
│       ├── header.html
│       ├── overview.html
│       └── index.html
├── doc
│   ├── architecture.png
│   ├── architecture.svg
│   ├── process.png
│   └── process.svg
├── LICENSE
├── README.md
├── reference-adapter
│   ├── 0100-add-one-entry.py
│   ├── 0101-add-million-entries.py
│   └── 0200-query-recent-tests.py
├── run.py
├── setup.py
└── TODO.md
```

# Further Information #

## REST ##

[Building RESTful API with flask](http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)

## Nice Timeline ##

http://www.bootply.com/106768#

Dynamic Timelime:

http://codyhouse.co/gem/vertical-timeline/

# Data Compression #

DOC file compression with python 

```
import gzip
import shutil

with open('9.pdf', 'rb') as f_in, gzip.open('9.pdf.gz', 'wb') as f_out:
	shutil.copyfileobj(f_in, f_out)
```

DOC 1,1M -> 429K in 0.19s
PDF 11M -> 7,2M in 0,38s

Compression on mime type (jpeg no gain, etc) and data size: if data size < 100k compression benefit low.
