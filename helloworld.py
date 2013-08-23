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

def sudokubook_key(sudokubook_name=None):
	"""Constructs a Datastore key for a Guestbook entity with sudokubook_name."""
	return db.Key.from_path('Guestbook', sudokubook_name or 'default_sudokubook')


class MainPage(webapp.RequestHandler):

	def get(self):
		self.response.out.write('<html><body>')
		sudokubook_name='cs496'

		sudokus = db.GqlQuery("SELECT * "
							"FROM Sudoku "
							"WHERE ANCESTOR IS :1 "
							"ORDER BY date DESC LIMIT 10",
							sudokubook_key('cs496'))

		for sudoku in sudokus:
			self.response.out.write('<p>Puzzle List:<br/> %s</p>'%cgi.escape(sudoku.puzzle))
			self.response.out.write('<a href="/puzz?'+(urllib.urlencode({"puzz":sudoku.puzzle}))+'">Solve</a>')

		self.response.out.write("""
			<form action="/sign?%s" method="post">
				<div><textarea name="puzzle" rows="3" cols="60"></textarea></div>
				<div><input type="submit" value="Enter sudoku"></div>
			</form>
		</body>
		</html>"""%(urllib.urlencode({'sudokubook_name': sudokubook_name})))

class SolveHandler(webapp.RequestHandler):
	def get(self):
		sudokus = db.GqlQuery("SELECT * "
							"FROM Sudoku "
							"WHERE ANCESTOR IS :1 "
							"ORDER BY date DESC LIMIT 10",
							 sudokubook_key('cs496'))

		for sudoku in sudokus:
			self.response.out.write('<p>%s</p>'%cgi.escape(sudoku.puzzle))
			if sudoku.solved_puzzle == None:
				solve(sudoku.puzzle)
				sudoku.solved_puzzle = puzzleAnswer	
				sudoku.put()
	
			self.response.out.write('<p>%s<p>'%sudoku.solved_puzzle)

	def post(self):
		sudokubook_name = self.request.get('sudokubook_name')
		sudoku = Sudoku(parent=sudokubook_key(sudokubook_name))

		sudoku.puzzle = self.request.get('puzzle')
		sudoku.author = self.request.get('author')
		sudoku.solved_puzzle = None
		sudoku.put()

		self.redirect('/?' + urllib.urlencode({'sudokubook_name': sudokubook_name}))

class PuzzleSolver(webapp.RequestHandler):

	def get(self):
		puzzle = self.request.get('puzz')
		sudoku = db.GqlQuery("SELECT * "
							  "FROM Sudoku "
							  "WHERE ANCESTOR IS :1 "
							  "AND puzzle= :2",
							   sudokubook_key('cs496'), puzzle)

		for s in sudoku:
			#self.response.out.write(s.puzzle)
			if s.solved_puzzle == None:
				solve(puzzle)
				s.solved_puzzle=puzzleAnswer
				s.put()	

		for k in range (0, 81, 9):
			self.response.out.write(s.solved_puzzle[k+0:k+3] +
				 ' | ' + s.solved_puzzle[k+3:k+6] +
				 ' | ' + s.solved_puzzle[k+6:k+9]+'<br/>')
			if k is 18 or k is 45:
				self.response.out.write('---- + ---- + ----'+'<br/>')

		self.response.out.write('<br/>')

	def post(self):
		sudoku = Sudoku(parent=sudokubook_key('cs496'))
		sudoku.puzzle = self.request.get('puzzle')
		sudoku.author = self.request.get('author')
		sudoku.solved_puzzle = None
		sudoku.put()

		self.redirect('/?' + urllib.urlencode({'sudokubook_name': sudokubook_name}))


class Guestbook(webapp.RequestHandler):
  def post(self):
    sudokubook_name = 'cs496'
    sudoku = Sudoku(parent=sudokubook_key(sudokubook_name))

    if users.get_current_user():
      sudoku.author = users.get_current_user().nickname()

    sudoku.puzzle = self.request.get('puzzle')
    sudoku.put()
    self.redirect('/?' + urllib.urlencode({'sudokubook_name': sudokubook_name}))

application = webapp.WSGIApplication([
	('/', MainPage),
	('/sign', Guestbook),
	('/puzz', PuzzleSolver),
	('/solve', SolveHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
	
