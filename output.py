#!/opt/python-2.6/bin/python2.6
# Mami Sasaki and Nat Byington
# Ling572 output class

import sys

# struct table
class Struct:

    # default constructor 
    def __init__(self):
       self.cls = ''
       self.instance = ''
       self.features = '' 
       self.probs = {}

# output format class
class Matrix:

   # initialize matrix
   def __init__(self,class_type):
      # Initialize confusion matrix.
      self.__dict__ = dict( [(x, {}) for x in class_type] )
      for c in class_type:
          for c2 in class_type:
              self.__dict__[c][c2] = 0


   # getter function
   def get_value(self,i,j):
       return self.__dict__[i][j]


   # setter function
   def set_value(self,i,j,n):
       self.__dict__[i][j] = self.__dict__[i][j] + n


   # output acc file
   def output_acc(self,file_name,doc_count,class_probs):

      # Output to acc
      correct = 0.0
      print 'Confusion matrix for ' + file_name + ':'
      print 'row is the truth, column is the system output'
      print ''
      sys.stdout.write('\t\t')
      for c in class_probs:
          sys.stdout.write(' ' + c)
          correct += self.get_value(c,c)
      sys.stdout.write('\n')
      for c in class_probs:
          sys.stdout.write(c)
          for c2 in class_probs:
              sys.stdout.write(' ' + str(self.get_value(c,c2)))
          sys.stdout.write('\n')
      print ''
      print file_name + ' accuracy: ' + str(correct / doc_count)
      print ''

