import pytest
from qdjarv import Validator, Type, Rel, ValidationError


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

    validator = Validator(top="people", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response)

    validator = Validator(top=["people"], types=types)
    with pytest.raises(ValidationError):
        validator.validate(response)

    validator = Validator(top=["articles"], types=types)
    with pytest.raises(ValidationError):
        validator.validate(response)

    validator = Validator(top="articles", types=types)
    validator.validate(response)

    response2 = {
      "data": [{
        "type": "articles",
        "id": "1",
        "attributes": {"title": "JSON:API paints my bikeshed!"},
      }],
    }
    validator = Validator(top="articles", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response2)
    validator = Validator(top=["people"], types=types)
    with pytest.raises(ValidationError):
        validator.validate(response2)


def test_bad_rel_type():
    types = {
        "articles": {
            "comments": Rel("foo"),
        },
        "foo": {},
        "bar": {}
    }
    response = {
        "data": {
            "type": "articles",
            "id": "1",
            "relationships": {
                "comments": {
                    "data": {
                        "id": "1",
                        "type": "bar",
                    }
                }
            },
        },
    }
    validator = Validator(top="articles", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response)

    correct_types = {
        "articles": {
            "comments": Rel("bar"),
        },
        "foo": {},
        "bar": {}
    }
    validator = Validator(top="articles", types=correct_types)
    validator.validate(response)


def test_bad_rel_list_type():
    types = {
        "articles": {
            "comments": Rel(["bar"]),
        },
        "foo": {},
        "bar": {},
    }
    correct_types = {
        "articles": {
            "comments": Rel(["foo"]),
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
                    "data": [{
                        "id": "1",
                        "type": "foo",
                    }]
                }
            },
        },
    }
    validator = Validator(top="articles", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response)
    validator = Validator(top="articles", types=correct_types)
    validator.validate(response)


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

    validator = Validator(top="articles", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response)

    other_types = {
        "things": {}
    }

    validator = Validator(top="articles", types=other_types)
    with pytest.raises(ValidationError):
        validator.validate(response)

    full_types = {
        "articles": {
            "title": Type(str),
        },
        "things": {}
    }

    validator = Validator(top="articles", types=full_types)
    validator.validate(response)


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
    validator = Validator(top="articles", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response1)

    response2 = {
      "data": {
        "type": "articles",
        "id": "1",
      },
    }
    validator = Validator(top="articles", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response2)

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
    validator = Validator(top="articles", types=types_rel)
    with pytest.raises(ValidationError):
        validator.validate(response1_rel)

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
    validator = Validator(top="articles", types=types_rel)
    with pytest.raises(ValidationError):
        validator.validate(response2_rel)


def test_bad_field_type():
    types = {
        "articles": {
            "title": Type(str),
        },
    }
    response1 = {
      "data": {
        "type": "articles",
        "id": "1",
        "attributes": {
            "title": ["Hello", "world"]
        },
      },
    }
    validator = Validator(top="articles", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response1)

    response2 = {
      "data": {
        "type": "articles",
        "id": "1",
        "attributes": {
            "title": None
        },
      },
    }
    validator = Validator(top="articles", types=types)
    with pytest.raises(ValidationError):
        validator.validate(response2)


def test_custom_validation():
    def optional(t):
        def do(elem):
            if elem is None:
                return elem
            return Type(elem)
        return do

    types = {
        "articles": {
            "title": optional(str),
        },
    }
    response = {
      "data": {
        "type": "articles",
        "id": "1",
        "attributes": {
            "title": None
        },
      },
    }
    validator = Validator(top="articles", types=types)
    result = validator.validate(response)
    assert result["data"]["title"] is None
