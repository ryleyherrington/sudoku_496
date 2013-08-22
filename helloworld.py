import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#038796215659132478271458693845219367713564829926873154194325786362987541587641932

class Sudoku(db.Model):
	author = db.StringProperty()
	puzzle = db.StringProperty(multiline=True)
	solved_puzzle = db.StringProperty(multiline=True)
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
		guestbook_name='cs496'

		sudokus = db.GqlQuery("SELECT * "
							"FROM Sudoku "
							"WHERE ANCESTOR IS :1 "
							"ORDER BY date DESC LIMIT 10",
							guestbook_key('cs496'))

		for sudoku in sudokus:
			self.response.out.write('<p>UNSOLVED:<br/> %s</p>'%cgi.escape(sudoku.puzzle))

		self.response.out.write("""
				<form action="/sign?%s" method="post">
				<div><textarea name="puzzle" rows="3" cols="60"></textarea></div>
				<div><input type="submit" value="Solve Puzzle"></div>
				</form>
			</body>
			</html>""" % (urllib.urlencode({'guestbook_name': 'cs496'})))

class SolveHandler(webapp.RequestHandler):

	def get(self):
		sudokus = db.GqlQuery("SELECT * "
							"FROM Sudoku "
							"WHERE ANCESTOR IS :1 "
							"ORDER BY date DESC LIMIT 10",
							 guestbook_key('cs496'))

		for sudoku in sudokus:
			self.response.out.write('<p>%s</p>'%cgi.escape(sudoku.puzzle))
			if sudoku.solved_puzzle== 'a':
				solve(sudoku.puzzle)
				sudoku.solved_puzzle = puzzleAnswer	
	
			self.response.out.write('<p>%s<p>'%sudoku.solved_puzzle)

	def post(self):
		guestbook_name = self.request.get('guestbook_name')
		sudoku = Sudoku(parent=guestbook_key(guestbook_name))

		if users.get_current_user():
			sudoku.author = users.get_current_user().nickname()

		sudoku.puzzle = self.request.get('puzzle')
		sudoku.author = self.request.get('author')
		sudoku.solved_puzzle = 'a'
		sudoku.put()

		self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

application = webapp.WSGIApplication([
	('/', MainPage),
	('/solve', SolveHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
	
