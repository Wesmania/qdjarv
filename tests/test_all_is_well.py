from copy import deepcopy
from qdjarv import Parser, Type, Rel


types = {
    "articles": {
        "title": Type(str),
        "author": Rel("people"),
        "comments": Rel(["comments"]),
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


include = {
    "author": {},
    "comments": {},
}


response = {
  "links": {
    "self": "http://example.com/articles",
    "next": "http://example.com/articles?page[offset]=2",
    "last": "http://example.com/articles?page[offset]=10"
  },
  "data": [{
    "type": "articles",
    "id": "1",
    "attributes": {
      "title": "JSON:API paints my bikeshed!"
    },
    "relationships": {
      "author": {
        "links": {
          "self": "http://example.com/articles/1/relationships/author",
          "related": "http://example.com/articles/1/author"
        },
        "data": {"type": "people", "id": "9"}
      },
      "comments": {
        "links": {
          "self": "http://example.com/articles/1/relationships/comments",
          "related": "http://example.com/articles/1/comments"
        },
        "data": [
          {"type": "comments", "id": "5"},
          {"type": "comments", "id": "12"}
        ]
      }
    },
    "links": {
      "self": "http://example.com/articles/1"
    }
  }],
  "included": [{
    "type": "people",
    "id": "9",
    "attributes": {
      "firstName": "Dan",
      "lastName": "Gebhardt",
      "twitter": "dgeb"
    },
    "links": {
      "self": "http://example.com/people/9"
    }
  }, {
    "type": "comments",
    "id": "5",
    "attributes": {
      "body": "First!"
    },
    "relationships": {
      "author": {
        "data": {"type": "people", "id": "2"}
      }
    },
    "links": {
      "self": "http://example.com/comments/5"
    }
  }, {
    "type": "comments",
    "id": "12",
    "attributes": {
      "body": "I like XML better"
    },
    "relationships": {
      "author": {
        "data": {"type": "people", "id": "9"}
      }
    },
    "links": {
      "self": "http://example.com/comments/12"
    }
  }]
}


def test_all_is_well():
    parser = Parser(top=["articles"], types=types, include=include)
    mcopy = deepcopy(response)

    mcopy = parser.parse(mcopy)

    author_obj = mcopy["data"][0]

    assert author_obj["title"] == author_obj[".attributes"]["title"]
    assert author_obj["author"] == author_obj[".relationships"]["author"]
    assert author_obj["comments"] == author_obj[".relationships"]["comments"]

    assert author_obj["author"]["data"]["firstName"] == "Dan"
    assert author_obj["comments"]["data"][0]["body"] == "First!"

    assert mcopy["links"] == response["links"]
