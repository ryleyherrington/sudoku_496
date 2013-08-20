#!/usr/bin/env python

import webapp2
import cgi
import sys 

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

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
  

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""
    <html>
      <body>
        <form action="/solve" method="post">
          <div><textarea name="content" rows="10" cols="8"></textarea></div>
          <div><input type="submit" value="Solve"></div>
        </form>
      </body>
    </html>""")


class SolvedPage(webapp.RequestHandler):
  def post(self):
    puzzle = self.request.get('content')
	#should put puzzle into the datastore here
    solve(puzzle)
    self.response.out.write(puzzleAnswer)

    #self.response.out.write('<html><body>Unsolved Puzzle:<p></p>')
    #self.response.out.write(cgi.escape(puzzle))
    #self.response.out.write('<p></p> Solved Puzzle:<p></p>')
    #DELETE ABOVE LINE IF YOU UNCOMMENT self.response.out.write(puzzleAnswer)
    #self.response.out.write('<br></br>')
    #for k in range (0, 81, 9):
    #  self.response.out.write(puzzleAnswer[k+0:k+3] + ' | ' + puzzleAnswer[k+3:k+6] + ' | ' + puzzleAnswer[k+6:k+9]+'<br/>')
    #  if k is 18 or k is 45:
    #    self.response.out.write('---- + ---- + ----'+'<br/>')
    #self.response.out.write('</body></html>')


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/solve', SolvedPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
