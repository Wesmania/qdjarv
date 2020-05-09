from qdjarv import Parser, Rel


def test_relation_without_data():
    types = {
        "articles": {
            "comments": Rel(["bar"]),
        },
        "foo": {},
        "bar": {},
    }
    response = {
        "data": {
            "type": "articles",
            "id": "1",
            "relationships": {
                "comments": {
                    "links": "http://foo.bar"
                }
            },
        },
    }
    parser = Parser("articles", types)
    msg = parser.parse(response)

    assert "links" in msg["data"]["comments"]
    assert "data" not in msg["data"]["comments"]


def test_null_relation():
    types = {
        "articles": {
            "comments": Rel("bar"),
        },
        "foo": {},
        "bar": {},
    }
    response = {
        "data": {
            "type": "articles",
            "id": "1",
            "relationships": {
                "comments": {
                    "data": None
                }
            },
        },
    }
    parser = Parser("articles", types)
    msg = parser.parse(response)

    assert msg["data"]["comments"]["data"] is None
