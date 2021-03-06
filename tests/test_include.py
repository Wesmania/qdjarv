import pytest
from copy import deepcopy
from qdjarv import Validator, Rel, Type, ValidationError


def test_include_args():
    types = {
        "articles": {
            "author": Rel("people"),
            "comments": Rel(["comments"])
        },
        "people": {
            "articles": Rel(["articles"]),
            "comments": Rel(["comments"]),
        },
        "comments": {
            "author": Rel("people")
        }
    }

    include = {
        "author": {
            "articles": {},
            "comments": {},
        },
        "comments": {}
    }

    validator = Validator("articles", types, include=include)

    args = validator.include_args()
    assert set(args) == {"author", "author.articles", "author.comments",
                         "comments"}


def test_missing_includes():
    types = {
        "articles": {
            "author": Rel("people"),
            "comments": Rel(["comments"])
        },
        "people": {
            "foo": Type(str),
        },
        "comments": {
            "foo": Type(str),
        }
    }
    include = {
        "author": {},
        "comments": {},
    }

    response_data = {
        "type": "articles",
        "id": "1",
        "relationships": {
            "author": {
                "data": {
                    "id": "1",
                    "type": "people",
                }
            },
            "comments": {
                "data": [{
                    "id": "1",
                    "type": "comments",
                }]
            }
        },
    }
    response_1 = {
        "data": response_data,
        "included": [{
            "id": "1",
            "type": "comments",
            "attributes": {
                "foo": "bar"
            }
        }]
    }
    response_2 = {
        "data": response_data,
        "included": [{
            "id": "1",
            "type": "people",
            "attributes": {
                "foo": "bar"
            }
        }]
    }
    response_3 = {
        "data": response_data,
        "included": [
            {
                "id": "1",
                "type": "people",
                "attributes": {
                    "foo": "bar"
                }
            },
            {
                "id": "1",
                "type": "comments",
                "attributes": {
                    "foo": "bar"
                }
            }
        ]
    }

    validator = Validator("articles", types, include=include)
    with pytest.raises(ValidationError):
        validator.validate(deepcopy(response_1))
    with pytest.raises(ValidationError):
        validator.validate(deepcopy(response_2))
    validator.validate(deepcopy(response_3))


def test_include_field_without_data():
    types = {
        "articles": {
            "author": Rel("people"),
        },
        "people": {
            "foo": Type(str),
        },
    }
    include = {
        "author": {},
    }

    response = {
        "data": {
            "type": "articles",
            "id": "1",
            "relationships": {
                "author": {
                    "links": "foobar"
                },
            },
        }
    }
    validator = Validator("articles", types)
    validator.validate(deepcopy(response))

    validator = Validator("articles", types, include=include)
    with pytest.raises(ValidationError):
        validator.validate(deepcopy(response))


def test_include_null_field():
    types = {
        "articles": {
            "author": Rel("people"),
        },
        "people": {
            "foo": Type(str),
        },
    }
    include = {
        "author": {},
    }

    response = {
        "data": {
            "type": "articles",
            "id": "1",
            "relationships": {
                "author": {
                    "links": "foobar",
                    "data": None
                },
            },
        }
    }
    validator = Validator("articles", types, include=include)
    msg = validator.validate(deepcopy(response))
    assert msg["data"]["author"]["data"] is None
