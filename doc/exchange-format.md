
# Concept and Architecture #

This document describes the internal and external API of contestcolld.
Understanding this document provides nearly all required information how
contestcolld works internally, how contestcolld can be extended and what are
the basic concept behind contestcolld.

## Object Issue ##

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

* description
* categories
* version
* data

```
{
	"description" : "Check that the route cache is flushed after NIC change",
	"categories": [ "team:red", "topic:ip", "subtopic:route-cache" ],
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

#### Description ####


#### Categories ####

Categories are ordered in the list. A Object issue MUST specify at least one
categories but can specify more. Categories are the mechanism to group test to
teams or functional aspects. Categories are a powerfull and flexible mechanism
for grouping.

If you have no categories because the project is small you can use "common".

#### Version ####

Version can be 0.

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

	"_serial": 0
}
```


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
	"media":      [
	  {
			"description": "image of the routing architecture and test setup"
			"mime-type":   "media/png",
			"data":        "<base64 encoded image>"
		},
	],
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
			"mime-type":   "binary/octet-stream",
			"data":        "<base64 encoded data>"
		}
	]
}
```

### Required Attributes ###

* name
* date
* result

### Optional Attributes

Optional attributes are evaluated if available. 

* sender-id
* data

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
			"data": <OBJECT ACHIEVEMENT>
		},
		{
			"id": 2,
			"date-uploaded": "date when stored in database, not user provided date",
			"data": <OBJECT ACHIEVEMENT>
		},
	]
}
```

The object-id is the SHA256 of the object-issue. But the object container can
only contain one particular object-issue. To identify a object-container
exactly the SHA256 of the object-issue is the ideal key.

Object achievement IDs are incremented at each new added achievement.


## Release Label ##

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

# Database File Layout #

db/object-issues/
db/release-labels.db

## Typical Layout after some entries ##

db/object-issues/35
db/object-issues/35/
db/object-issues/35/358548239f0593.db
db/object-issues/f1/
db/object-issues/f1/f1048a91949a32.db
db/object-issues/f1/f1b19d018a4801.db
db/object-issues/2a
db/object-issues/2a/2a58ab18348219.db
db/release-labels.db
