import os
import urllib

from boilerplate import BaseHandler
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

from wordnik import *
import random


WORDNIK_AUTH = 'a5bd15f58170c3006090b04ce940cfa55794ee7e545440599'
WORDNIK_API = 'http://api.wordnik.com/v4'
UNACCEPTABLES = ["alternative form","plural form", "spelling",
                 "present participle", "simple present", "past participle",
                 "present simple"]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/sign?%s" method="post">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Sign Guestbook"></div>
    </form>

    <hr>

    <form>Guestbook name:
      <input value="%s" name="guestbook_name">
      <input type="submit" value="switch">
    </form>

    <a href="%s">%s</a>

  </body>
</html>
"""

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'
DEFAULT_WORDSET_LIMIT = 6


client = swagger.ApiClient(WORDNIK_AUTH, WORDNIK_API)
WORDSAPI = WordsApi.WordsApi(client)
WORDAPI = WordApi.WordApi(client)
# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)


class Greeting(ndb.Model):
    """Models an individual Guestbook entry with author, content, and date."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class WordIndex(ndb.Model):
    id = ndb.StringProperty(indexed=True)
    definitions = ndb.JsonProperty(indexed=False)

class WordSet(ndb.Model):
    """ Collection of WordIndex Objects  """
    dictionary = ndb.StructuredProperty(WordIndex, repeated=True)

class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        valid = 0
        random_words = []
        word_set = WordSet()

        while valid < DEFAULT_WORDSET_LIMIT:
            new_limit = DEFAULT_WORDSET_LIMIT-valid
            print "CALLING WITH LIMIT=", new_limit
            if not new_limit%2:
                random_words = WORDSAPI.getRandomWords(limit=(new_limit/2),
                                                       includePartOfSpeech='noun')
                random_words += WORDSAPI.getRandomWords(limit=(new_limit/2),
                                                       includePartOfSpeech='verb')
            else:
                random_words = WORDSAPI.getRandomWords(limit=new_limit)

            print "Random_words: ", random_words

            print type(WORDAPI.getDefinitions('cat'))
            for w in random_words:
                found_unacceptable = False
                word_index = WordIndex(id=w.word)
                word_definitions = []
                for definition in WORDAPI.getDefinitions(w.word):
                    if [w for w in UNACCEPTABLES if w in definition.text.lower()]:
                        print "FOUND UNACEPTABLE. "
                    else:
                        print "TYPE: ", type(definition)
                        word_definitions.append(definition)


                word_index.definitions = [d.text for d in word_definitions]

                if len(word_index.definitions):
                    valid += 1
                    print "adding ", word_index.id , "to wordset"
                    word_set.dictionary.append(word_index)

        word_set.put()
        print "blah , word_set:", word_set

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'greetings': greetings,
            'guestbook_name': guestbook_name,
            'url': url,
            'url_linktext': url_linktext,
            'words': word_set
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)
