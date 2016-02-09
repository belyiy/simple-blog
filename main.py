import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_BLOG_NAME = 'default_post'


def blog_key(blog_name=DEFAULT_BLOG_NAME):
    return ndb.Key('Post', blog_name)


class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)


class Post(ndb.Model):
    author = ndb.StructuredProperty(Author)
    postdate = ndb.DateTimeProperty(auto_now_add=True)
    title = ndb.StringProperty(indexed=False)
    body = ndb.StringProperty(indexed=False)


class MainPage(webapp2.RequestHandler):
    def get(self):
        blog_name = self.request.get('post_name',
                                          DEFAULT_BLOG_NAME)
        posts_query = Post.query(
            ancestor=blog_key(blog_name)).order(-Post.postdate)
        posts = posts_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'posts': posts,
            'guestbook_name': urllib.quote_plus(blog_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class NodeAdd(webapp2.RequestHandler):
    def post(self):
        blog_name = self.request.get('post_name',
                                          DEFAULT_BLOG_NAME)
        blog = Blog(parent=blog_key(blog_name))

        if users.get_current_user():
            blog.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        blog.title = self.request.get('title')
        blog.date = self.request.get('postdate')
        blog.content = self.request.get('body')
        blog.put()

        template_values = {
            'user': user,
            'posts': posts,
            'guestbook_name': urllib.quote_plus(blog_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template("node.html")
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/node/add', NodeAdd),
], debug=True)
