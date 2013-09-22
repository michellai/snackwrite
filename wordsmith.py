
from google.appengine.ext import ndb

class WordIndex(ndb.Model):
    id = ndb.StringProperty(indexed=True)
    definitions = ndb.JsonProperty(indexed=False)

class WordSet(ndb.Model):
    """ Collection of WordIndex Objects  """
    dictionary = ndb.StructuredProperty(WordIndex, repeated=True)
