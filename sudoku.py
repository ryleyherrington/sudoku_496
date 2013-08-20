#!/usr/bin/env python
import cgi
import sys
import copy

puzzleAnswer = '0'

def same_row(i,j): return (i/9 == j/9)
def same_col(i,j): return (i-j) % 9 == 0
def same_square(i,j): return (i/27 == j/27 and i%9/3 == j%9/3)

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
   value    = {}

def printBoard(b):
   for k in range (0, 81, 9):
      print b.value[k+0], b.value[k+1], b.value[k+2], " | ",
      print b.value[k+3], b.value[k+4], b.value[k+5], " | ",
      print b.value[k+6], b.value[k+7], b.value[k+8]
      if k==18 or k==45 or k==72:
         print

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
      #print 'setUniqueInBoard: Checking all 9 rows      : change = ', change
      for k in range(0, 81, 9):
         if setUniqueCells(b, row(k)):
            change = True
      #print 'setUniqueInBoard: Checking all 9 columns   : change = ', change
      for k in range (9):
         if setUniqueCells(b, col(k)):
            change = True
      #print 'setUniqueInBoard: Checking all 9 squares   : change = ', change
      for k in range(0, 81,27):
         for j in range(k, k+9, 3):
            if setUniqueCells(b, square(j)):
               change = True

def markCell(b, position, val):
   #print "markCell(", position, ",", val, ")  value[position] == ", b.value[position], " possible[position] == ", b.possible[position]
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
   #print "setCell(", position, ",", newVal, ")  value[position] == ", b.value[position], " possible[position] == ", b.possible[position]
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
   
def solve(a):
  global puzzleAnswer

  i = a.find('0')
  if i==-1:
    puzzleAnswer=a

  excluded = set()
  for j in range(81):
    if same_row(i,j) or same_col(i,j) or same_square(i,j):
      excluded.add(a[j])

  for n in '123456789':
    if n not in excluded:
      solve(a[:i]+n+a[i+1:])


if __name__ == '__main__':
   if len(sys.argv) == 2 and len(sys.argv[1]) == 81:
      b = Board()
      partialSolve(b, sys.argv[1])
      printBoard(b)
   else:
      print 'Usage: sudoku.py numbers'
      print ' where numbers means an 81 character string. Left-->right, top-->bottom, and 0 means unknown'


