
# Concept and Architecture #

This document describe the internal and external API of contestcolld.
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

```
{
	"description" : "Foo bar",
	"categories": ["rpp", "ip"],

	[ optional attributes ]
}
```

#### Categories ####

Categories are ordered in the list. A Object issue MUST specify at least one
categories but can specify more. Categories are the mechanism to group test to
teams or functional aspects. Categories are a powerfull and flexible mechanism
for grouping.



If you have no categories because the project is small you can use "common".

### Optional Attributes ###

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
	"media":      [ "image/svg+xml:base64encodedsvg", image/png:base64encodedpng ]
	"references": [ "doors:234234", "doors:4391843" ],
	"replaces":   [ "14d348a14934a02034b", "43348a234434934f0203421" ],
	"tags":       [ "ip", "tcp", "stack" ],
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
	"sender-id" : "windows-workgroups-foo",
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
	"object-attachment-id": 8f348a14934f302034a
	"object-attachment" : <OBJECT>,
	"date-added": 12-21-2013,
	object-achievements = [
	]
}
```


## Release Label ##
