#!/usr/bin/env python

#import webapp2
import cgi
import sys 

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

def same_row(i,j): return (i/9 == j/9)
def same_col(i,j): return (i-j) % 9 == 0
#Divide it into thirds and then figure out if they are in the same
#box column/row (that's the %9/3 part).
def same_square(i,j): return (i/27 == j/27 and i%9/3 == j%9/3)

#set global variable puzzle answer to dummy variable of same type as answer
puzzleAnswer = '0'

def solve(a):
  #make reference to the global puzzleAnswer for the rest of the method
  #otherwise we are not able to change it (after we exit puzzleAnswers=0)
  global puzzleAnswer

  #find the first unknown digit
  i = a.find('0')
  #if no zero's exist, we are done solving.
  if i==-1:
    #set the global answer to our solved puzzle
    puzzleAnswer = a
  
  excluded = set()
  for j in range(81):
    #checking to make sure our number we try is not in the same ____
    if same_row(i,j) or same_col(i,j) or same_square(i,j):
      #if it is in the same row/col/square then add to excluded set
      excluded.add(a[j])

  for n in '123456789':
    if n not in excluded:
      #recursive call to put the number we found into the space and then
      #reconstruct our list of numbers. a[:i] means a from 0->i then add our
      #number to the list instead of zero, then construct it from a[i+1: end of list]
      solve(a[:i]+n+a[i+1:])
  

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""
    <html>
      <body>
        <form action="/sign" method="post">
          <div><textarea name="content" rows="10" cols="8"></textarea></div>
          <div><input type="submit" value="Solve"></div>
        </form>
      </body>
    </html>""")


class SolvedPage(webapp.RequestHandler):
  def post(self):
    puzzle = self.request.get('content')
     
    self.response.out.write('<html><body>Unsolved Puzzle:<p></p>')
    #cgi.escape is to make the html string safe to put on the side without
    #interpretation. Safety first. See here for a complete example:
    #https://developers.google.com/appengine/docs/python/gettingstarted/handlingforms  
    self.response.out.write(cgi.escape(puzzle))
    self.response.out.write('<p></p> Solved Puzzle:<p></p>')
    solve(puzzle)
    self.response.out.write(puzzleAnswer)
    self.response.out.write('<br></br>')
    for k in range (0, 81, 9):
      self.response.out.write(puzzleAnswer[k+0:k+3] + ' | ' + puzzleAnswer[k+3:k+6] + ' | ' + puzzleAnswer[k+6:k+9]+'<br/>')
      if k is 18 or k is 45:
        self.response.out.write('---- + ---- + ----'+'<br/>')
    self.response.out.write('</body></html>')


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', SolvedPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
