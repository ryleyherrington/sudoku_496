#Copyright 2013 by Ryley Herrington
import cgi
import datetime
import urllib
import wsgiref.handlers

from datetime import datetime, timedelta
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#038796215659132478271458693845219367713564829926873154194325786362987541587641932

class Sudoku(db.Model):
	author = db.StringProperty()
	puzzle = db.StringProperty(multiline=True)
	solved_puzzle = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

def row(i):
	r=(i//9)*9
	return [ r, r+1, r+2, r+3, r+4, r+5, r+6, r+7, r+8 ]

def col(i):
	c=(i%9)
	return [c, c+9, c+18, c+27, c+36, c+45, c+54, c+63, c+72 ]

def square(i):
	s=(i//27)*27 + (((i%9)//3)*3)
	return [s, s+1, s+2, s+9, s+10, s+11, s+18, s+19, s+20 ]

class Board:
	possible = {}
	value	 = {}

def setUniqueCells(b, cells):
	found_change = False
	all_possibles = ""
	for c in cells:
		if int(b.value[c]) == 0:
			all_possibles = all_possibles + b.possible[c]
	for v in "123456789":
		if int(all_possibles.count(v)) == 1:
			for c in cells:
				if int(b.possible[c].count(v) == 1) and int(b.value[c]) == 0:
					setCell(b, c, v)
					found_change = True
	return found_change

def setUniqueInBoard(b):
	change = True
	while change == True:
		change = False
		for k in range(0, 81, 9):
			if setUniqueCells(b, row(k)):
				change = True
		for k in range (9):
			if setUniqueCells(b, col(k)):
				change = True
		for k in range(0, 81,27):
			for j in range(k, k+9, 3):
				if setUniqueCells(b, square(j)):
					change = True

def markCell(b, position, val):
	if int(b.value[position]) == 0:
		p = b.possible[position]
		i = p.find(val)
		if i == 0:
			p = p[1:]
		elif i != -1:
			p = p[:i] + p[i+1:]
		b.possible[position] = p
		if int(b.value[position]) == 0 and int(len(p)) == 1:
			setCell(b, position, p[0])
	

def setCell(b, position, newVal):
	if int(b.value[position]) == 0:
		b.value[position] = newVal
		if newVal != '0':
			b.possible[position] = newVal
			for x in row(position):
				if (x != position):
					markCell(b, x, newVal)
			for x in col(position):
				if (x != position):
					markCell(b, x, newVal)
			for x in square(position):
				if (x != position):
					markCell(b, x, newVal)

def partialSolve(b, line):
	for i in range(81):
		b.possible[i] = "123456789"
		b.value[i] = '0'
	position=0
	for val in line:
		if val is not '0':
			setCell(b, position, val)
		position = position + 1
	setUniqueInBoard(b)


def sudokubook_key(sudokubook_name=None):
	return db.Key.from_path('Guestbook', sudokubook_name or 'default_sudokubook')

def prettyPrint(puzzle):
    answer = ''
    for k in range (0, 81, 9):
        answer = answer + puzzle[k+0:k+3] + ' | ' + puzzle[k+3:k+6] + ' | ' + puzzle[k+6:k+9]+'<br/>'
        if k is 18 or k is 45:
            answer =answer + '---- + ---- + ----'+'<br/>'

    answer = answer+'<br/>'
    return answer


class MainPage(webapp.RequestHandler):

	def get(self):
		self.response.out.write('<html><body>')
		sudokubook_name='cs496'

		sudokus = db.GqlQuery("SELECT * "
							"FROM Sudoku "
							"ORDER BY date DESC LIMIT 10")

		for sudoku in sudokus:
			if sudoku.author == None:
				sudoku.author = "Anonymous"
			self.response.out.write(sudoku.author+" wanted to solve this puzzle:</br>")
			self.response.out.write(prettyPrint(sudoku.puzzle))
			self.response.out.write('<a href="/puzz?'+(urllib.urlencode({"puzz":sudoku.puzzle}))+'">Solve</a><br/>')

		self.response.out.write("""
			<form action="/?%s" method="post">
				<div><textarea name="puzzle" rows="3" cols="60"></textarea></div>
				<div><input type="submit" value="Enter sudoku"></div>
			</form>
		</body>
		</html>"""%(urllib.urlencode({'sudokubook_name': sudokubook_name})))

	def post(self):
		sudokubook_name = 'cs496'
		sudoku = Sudoku(parent=sudokubook_key(sudokubook_name))
		sudoku.puzzle = self.request.get('puzzle')
		sudoku.put()

		self.redirect('/')


class SolveHandler(webapp.RequestHandler):
	def get(self):
		sudokus = db.GqlQuery("SELECT * "
							"FROM Sudoku "
							"WHERE ANCESTOR IS :1 "
							"ORDER BY date DESC LIMIT 10",
							 sudokubook_key('cs496'))

		for sudoku in sudokus:
			if sudoku.solved_puzzle == None:
				b = Board()
				partialSolve(b, sudoku.puzzle)
				fullAnswer = ''
				for k in range (0, 81):
					fullAnswer = fullAnswer + b.value[k]
				sudoku.solved_puzzle = fullAnswer
				sudoku.put()
	
			self.response.out.write('<p>%s<p>'%prettyPrint(sudoku.solved_puzzle))

	def post(self):
		sudokubook_name = 'cs496'
		sudoku = Sudoku(parent=sudokubook_key(sudokubook_name))

		sudoku.puzzle = self.request.get('puzzle')
		sudoku.author = "Anonymous"
		sudoku.author = self.request.get('author')
		sudoku.solved_puzzle = None
		sudoku.put()

		self.redirect('/view?author=' + sudoku.author)

class ViewHandler(webapp.RequestHandler):
	def get(self):
		author = "Anonymous"
		author = self.request.get('author')
		sudoku = db.GqlQuery("SELECT * "
							 "FROM Sudoku "  
							 "WHERE author =:1 LIMIT 1 ", author)  
		for s in sudoku:
			if s.solved_puzzle == None:
				b = Board()
				partialSolve(b, s.puzzle)
				fullAnswer = ''
				for k in range (0, 81):
					fullAnswer = fullAnswer + b.value[k]
				s.solved_puzzle = fullAnswer
				s.put()	

			puzzle = ''
			puzzle = s.solved_puzzle	

		response = ''
		for k in range (0, 81, 9):
			response = response + puzzle[k+0:k+3] + ' | ' + puzzle[k+3:k+6] + ' | ' + puzzle[k+6:k+9]+'\n'
			if k is 18 or k is 45:
				response =response + '---- + ---- + ----\n'
		self.response.out.write(response)

class PuzzleSolver(webapp.RequestHandler):
	def get(self):
		puzzle = self.request.get('puzz')
		sudoku = db.GqlQuery("SELECT * "
							  "FROM Sudoku "
							  "WHERE ANCESTOR IS :1 "
							  "AND puzzle= :2",
							   sudokubook_key('cs496'), puzzle)

		for s in sudoku:
			if s.solved_puzzle == None:
				b = Board()
				partialSolve(b, sudoku.puzzle)
				fullAnswer = ''
				for k in range (0, 81):
					fullAnswer = fullAnswer + b.value[k]
				sudoku.solved_puzzle = fullAnswer
				s.put()	

		for k in range (0, 81, 9):
			self.response.out.write(s.solved_puzzle[k+0:k+3] +
				 ' | ' + s.solved_puzzle[k+3:k+6] +
				 ' | ' + s.solved_puzzle[k+6:k+9]+'<br/>')
			if k is 18 or k is 45:
				self.response.out.write('---- + ---- + ----'+'<br/>')

		self.response.out.write('<br/>')

class CronHandler(webapp.RequestHandler):
	def get(self):
		sudokus = db.GqlQuery("SELECT * "
							  "FROM Sudoku")

		for sudoku in sudokus:
			if sudoku.date < datetime.now() - timedelta(minutes=5):
				sudoku.delete()

application = webapp.WSGIApplication([
	('/', MainPage),
	('/puzz', PuzzleSolver),
	('/view', ViewHandler),
	('/solve', SolveHandler),
	('/cron', CronHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
	
