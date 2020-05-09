import pytest
from qdjarv import Parser, Type, Rel, ValidationError


def test_fields_work():
    types = {
        "articles": {
            "title": Type(str),
            "body": Type(str),
        },
    }
    response = {
      "data": {
        "type": "articles",
        "id": "1",
        "attributes": {"title": "JSON:API paints my bikeshed!"},
      },
    }

    fields = {"articles": ["title"]}

    parser = Parser(top="articles", types=types, fields=fields)
    res = parser.parse(response)

    assert "title" in res["data"]


def test_fields_missing_field():
    types = {
        "articles": {
            "title": Type(str),
            "body": Type(str),
        },
    }
    response = {
      "data": {
        "type": "articles",
        "id": "1",
        "attributes": {"body": "JSON:API paints my bikeshed!"},
      },
    }

    fields = {"articles": ["title"]}

    parser = Parser(top="articles", types=types, fields=fields)
    with pytest.raises(ValidationError):
        parser.parse(response)


def test_rel_fields():
    types = {
        "articles": {
            "title": Type(str),
            "comments": Rel(["comments"])
        },
        "comments": {
            "foo": Type(str),
            "bar": Type(str),
        }
    }
    response = {
        "data": {
            "type": "articles",
            "id": "1",
            "relationships": {
                "comments": {
                    "data": [{
                        "id": "1",
                        "type": "comments",
                    }]
                }
            },
        },
        "included": [{
            "type": "comments",
            "id": "1",
            "attributes": {
                "foo": "baz"
            }
        }]
    }

    fields = {"articles": ["comments"], "comments": ["foo"]}

    parser = Parser(top="articles", types=types, fields=fields)
    res = parser.parse(response)
    assert res["data"]["comments"]["data"][0]["foo"] == "baz"


def test_fields_args():
    types = {
        "articles": {
            "title": Type(str),
            "comments": Rel(["comments"])
        },
        "comments": {
            "foo": Type(str),
            "bar": Type(str),
        }
    }
    fields = {"articles": ["comments"], "comments": ["foo", "bar"]}
    parser = Parser(top="foo", types=types, fields=fields)
    attrs = parser.fields_args()
    assert set(attrs) == {"fields[articles]=comments",
                          "fields[comments]=foo,bar"}
