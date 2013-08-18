#!/usr/bin/python
import sys

def same_row(i,j): return (i/9 == j/9)
def same_col(i,j): return (i-j) % 9 == 0
def same_square(i,j): return (i/27 == j/27 and i%9/3 == j%9/3)

def r(a):
  i = a.find('0')
  if i==-1:
    sys.exit(a)

  excluded = set()
  for j in range(81):
    if same_row(i,j) or same_col(i,j) or same_square(i,j):
      excluded.add(a[j])

  for n in '123456789':
    if n not in excluded:
      #By now, n is not excluded by any row, column, or square, so place it and start on the next 0
      r(a[:i]+n+a[i+1:])

if __name__ == '__main__':
  if len(sys.argv) == 2 and len(sys.argv[1]) == 81:
    r(sys.argv[1])
  else:
    print 'Usage:sudoku.py numbers'
    print ' where numbers means an 81 character string. Left-->right, top-->bottom, and 0 means unknown'
