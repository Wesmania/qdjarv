import pytest
from qdjarv import Parser, Type, Rel, ValidationError


def test_bad_top_type():
    types = {
        "articles": {
            "title": Type(str),
        },
        "people": {
            "firstName": Type(str),
        }
    }
    response = {
      "data": {
        "type": "articles",
        "id": "1",
        "attributes": {"title": "JSON:API paints my bikeshed!"},
      },
    }

    parser = Parser(top="people", types=types)
    with pytest.raises(ValidationError):
        parser.parse(response)

    parser = Parser(top=["people"], types=types)
    with pytest.raises(ValidationError):
        parser.parse(response)

    parser = Parser(top=["articles"], types=types)
    with pytest.raises(ValidationError):
        parser.parse(response)

    parser = Parser(top="articles", types=types)
    parser.parse(response)

    response2 = {
      "data": [{
        "type": "articles",
        "id": "1",
        "attributes": {"title": "JSON:API paints my bikeshed!"},
      }],
    }
    parser = Parser(top="articles", types=types)
    with pytest.raises(ValidationError):
        parser.parse(response2)
    parser = Parser(top=["people"], types=types)
    with pytest.raises(ValidationError):
        parser.parse(response2)


def test_missing_type():
    types = {
        "articles": {
            "title": Type(str),
        },
    }
    response = {
      "data": {
        "type": "articles",
        "id": "1",
        "attributes": {"title": "JSON:API paints my bikeshed!"},
      },
      "included": [{
          "type": "things",
          "id": "1",
      }]
    }

    parser = Parser(top="articles", types=types)
    with pytest.raises(ValidationError):
        parser.parse(response)

    other_types = {
        "things": {}
    }

    parser = Parser(top="articles", types=other_types)
    with pytest.raises(ValidationError):
        parser.parse(response)

    full_types = {
        "articles": {
            "title": Type(str),
        },
        "things": {}
    }

    parser = Parser(top="articles", types=full_types)
    parser.parse(response)


def test_missing_fields():
    types = {
        "articles": {
            "title": Type(str),
        },
    }
    response1 = {
      "data": {
        "type": "articles",
        "id": "1",
        "attributes": {},
      },
    }
    parser = Parser(top="articles", types=types)
    with pytest.raises(ValidationError):
        parser.parse(response1)

    response2 = {
      "data": {
        "type": "articles",
        "id": "1",
      },
    }
    parser = Parser(top="articles", types=types)
    with pytest.raises(ValidationError):
        parser.parse(response2)

    types_rel = {
        "articles": {
            "comments": Rel("comments")
        },
        "comments": {}
    }

    response1_rel = {
      "data": {
        "type": "articles",
        "id": "1",
      },
    }
    parser = Parser(top="articles", types=types_rel)
    with pytest.raises(ValidationError):
        parser.parse(response1_rel)

    response2_rel = {
      "data": {
        "type": "articles",
        "id": "1",
        "relationships": {
            "things": {
                "data": {
                    "type": "comments",
                    "id": "1"
                }
            }
        }
      },
    }
    parser = Parser(top="articles", types=types_rel)
    with pytest.raises(ValidationError):
        parser.parse(response2_rel)
