Quick and dirty jsonapi response validator
==========================================

A library for validating jsonapi responses and simplifying their handling.

What it does:

* Validates that types have the fields you want, of the type you want.
* Links resources together.
* Validates that resources you wanted included, are included.
* Pulls up relationships and attributes one level up, to resource object level.

What it doesn't do:

* Validate that response is valid jsonapi. Use jsonapi's jsonschema.
* Build requests or handle http codes.
* ORM.

Usage
=====

Here's example usage:

```python
# Start by defining your types

from qdjarv import Parser, Type, Rel

# Field value can be any callable that either returns a validated value or
# throws.
# 'Type' just validates that the value is of a given type.

types = {
    "articles": {
        "title": Type(str),
        "author": Rel("people"),	# One-to-one relation.
        "comments": Rel(["comments"]),	# One-to-many relation.
    },
    "people": {
        "firstName": Type(str),
        "lastName": Type(str),
        "twitter": Type(str),
    },
    "comments": {
        "body": Type(str),
        "author": Rel("people")
    }
}

# If you're using sparse fields, define those, too.

fields = {
    "articles": ["title", "author"],
    "people": ["firstName", "lastName"]
}

# If you're using includes, also define them.
# This is equivalent to 'author,author.comments'.

include = {
    "author": {
        "comments": {}
    }
}

# Also declare your toplevel type.
top = ["articles"]  # This is a list, single element would be just "articles".

# Finally, create a parser.
p = Parser(top, types, include=include, fields=fields)

# Parsing modifies the received message, so make a copy if you want the
# original!
# Also remember to pass the message through jsonapi jsonschema first.
# If something goes wrong, it will throw a qdjarv.ValidationError.
parsed = p.parse(message)

# If you don't feel like repeating yourself, you can get your get parameters
# like so:
fields_args = p.fields_args()
include_args = p.include_args()
```

Here's an example parsed message:
```python
{
    # Other toplevel stuff skipped for brevity.
    "data": [
        {
            "type": "articles",
            "id": "1",

            # Relationships and attributes were pulled out to this level.
            # You might want to access links and meta (and maybe
            # relationships / attributes), so they're kept with a dot
            # prepended.
            ".links": {
            },
            ".meta": { # ...
            }
            ".relationships": { # ...
            }
            ".attributes": { # ...
            },

            "title": "JSON:API paints my bikeshed!"
            "author": {
                "links": {
                    # ...
                },
                "data": {
                    # If this resource was included, we replaced the binding
                    # with the object itself.
                    # Watch out for loops!
                    "type": "people",
                    "id": "9",
                    ".attributes": { # ...
                    },
                    ".links": { # ...
                    },
                    "firstName": "Dan",
                    "lastName": "Gebhardt",
                    "twitter": "dgeb"
                }
            },
            "comments": { # ...
            },
        }
    ],
    "included": [
        # Included objects are still here, in case you wanted them. Also linked
        # and flattened.
        {
            "type": "people",
            "id": "9",
            # ...
        },
        # ...
    ]
}

```

TODO
====

* Tests.
* Turning types into requests, maybe.
