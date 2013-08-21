import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class Sudoku(db.Model):
  """Models an individual Guestbook entry with an author, puzzle, and date."""
  author = db.StringProperty()
  puzzle = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


def same_row(i,j): return (i/9 == j/9)
def same_col(i,j): return (i-j) % 9 == 0
def same_square(i,j): return (i/27 == j/27 and i%9/3 == j%9/3)

puzzleAnswer = '0'

def solve(a):
  global puzzleAnswer

  i = a.find('0')
  if i==-1:
    puzzleAnswer = a
  
  excluded = set()
  for j in range(81):
    if same_row(i,j) or same_col(i,j) or same_square(i,j):
      excluded.add(a[j])

  for n in '123456789':
    if n not in excluded:
      solve(a[:i]+n+a[i+1:])

def guestbook_key(guestbook_name=None):
  """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')
    guestbook_name=self.request.get('guestbook_name')

    # Ancestor queries, as shown here, are strongly consistent; queries that
    # span entity groups are only eventually consistent. If we omitted the
    # ancestor from this query, there would be a slight chance that a sudoku
    # that had just been written would not show up in a query.
    sudokus = db.GqlQuery("SELECT * "
                            "FROM Sudoku "
                            "WHERE ANCESTOR IS :1 "
                            "ORDER BY date DESC LIMIT 10",
                            guestbook_key(guestbook_name))

    for sudoku in sudokus:
      if sudoku.author:
        self.response.out.write(
            '<b>%s</b> wrote:' % sudoku.author)
      else:
        self.response.out.write('An anonymous person wrote:')
      self.response.out.write('<blockquote>%s</blockquote>' %
                              cgi.escape(sudoku.puzzle))

    self.response.out.write("""
          <form action="/sign?%s" method="post">
            <div><textarea name="puzzle" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Solve Puzzle"></div>
          </form>
          <hr>
          <form>Guestbook name: <input value="%s" name="guestbook_name">
          <input type="submit" value="switch"></form>
        </body>
      </html>""" % (urllib.urlencode({'guestbook_name': guestbook_name}),
                          cgi.escape(guestbook_name)))


class Guestbook(webapp.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Sudoku' to ensure each sudoku is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
    guestbook_name = self.request.get('guestbook_name')
    sudoku = Sudoku(parent=guestbook_key(guestbook_name))

    if users.get_current_user():
      sudoku.author = users.get_current_user().nickname()

    sudoku.puzzle = self.request.get('puzzle')
    sudoku.put()
    self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))



application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/sign', Guestbook),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
  main()
	
