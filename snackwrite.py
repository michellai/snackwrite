import os
import urllib
import cgi

from boilerplate import BaseHandler
from wordsmith import WordIndex, WordSet
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
    <form action="/?%s" method="post">
      <input value="%s" name="author_name">
      <input type="submit" value="login">
    </form>

    <a href="%s">%s</a>

  </body>
</html>
"""

DEFAULT_CONTEST_WORD = 'cherries'
DEFAULT_AUTHOR_NAME = 'cherries'
DEFAULT_WORDSET_LIMIT = 6


client = swagger.ApiClient(WORDNIK_AUTH, WORDNIK_API)
WORDSAPI = WordsApi.WordsApi(client)
WORDAPI = WordApi.WordApi(client)
# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

DEFAULT_GUESTBOOK_NAME = 'cherries'
def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)


class Greeting(ndb.Model):
    """Models an individual Guestbook entry with author, content, and date."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

def contest_key(contest_word=DEFAULT_CONTEST_WORD):
    """Constructs a Datastore key for a SnackWrite entity with contest_word."""
    return ndb.Key('Contest', contest_word)

class SnackEntry(ndb.Model):
    """Models an individual Snackwrite entry with author, content, and date."""
    author = ndb.StringProperty(indexed=True)
    genre = ndb.StringProperty(indexed=True)
    content = ndb.StringProperty(indexed=False)
    contest_word = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    opponent_key = ndb.KeyProperty()
    votes = ndb.IntegerProperty(indexed=False)

class MainPage(webapp2.RequestHandler):
    def get(self):
        """"
        user = users.get_current_user()

        if users.get_current_user():
            self.response.write('Hello, ' + user.nickname())
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

        else:
            self.redirect(users.create_login_url(self.request.uri))
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        author_name = users.get_current_user().nickname()
        sign_query_params = urllib.urlencode({'author': author_name})
        """

        template = JINJA_ENVIRONMENT.get_template('choices.html')
        self.response.write(template.render())


class WritePage(webapp2.RequestHandler):
    def get(self):
        contest_word = self.request.get('contest_word', DEFAULT_CONTEST_WORD)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'contest_word': contest_word,
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('writepage.html')
        self.response.write(template.render(template_values))

    def post(self):
        contest_word = self.request.get('contest_word',
                                          DEFAULT_CONTEST_WORD)
        snackentry = SnackEntry(parent=contest_key(contest_word))

        snackentry.author = self.request.get('author')

        snackentry.content = self.request.get('content')
        snackentry.contest_word = contest_word
        snackentry.put()

        #redirect somewhere better...
        query_params = {'contest_word': contest_word}
        self.redirect('/?' + urllib.urlencode(query_params))

class WordPage(webapp2.RequestHandler):
    def get(self):
        contest_word = self.request.get('contest_word', DEFAULT_CONTEST_WORD)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        definition = 'plural of small, round stone fruit that is typically bright or dark red.'
        template_values = {
            'url': url,
            'url_linktext': url_linktext,
            'contest_word': contest_word,
            'definition': definition
        }
        template = JINJA_ENVIRONMENT.get_template('wordpage.html')
        self.response.write(template.render(template_values))

class DecisionPage(webapp2.RequestHandler):

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
    ('/choose', DecisionPage),
    ('/word', WordPage),
    ('/write', WritePage),
    ('/sign', Guestbook),
], debug=True)
