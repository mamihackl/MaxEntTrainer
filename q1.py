#!/usr/bin/env python2.6
#Mami Hackl
#Nat Byington
#572 hw7q1: 1-vs-all 

import sys,re,output,os,subprocess

class map:
  
      def __init__(self):
          self.total = 0
          self.index = {} 

TERMS = set()

#sort data
def sort_data(file,train):

   # sort features
   table_list = []

   if train:
     #class map
     map_list = map()

   #read data line by line
   for l in file.readlines():
       newl = re.match('^(\S+) (\S+) (.*)', l)
       f_list = re.findall('(\w+) (\d+)', l)

       #create table
       table = output.Struct()
       table.instance = newl.group(1)
       table.cls = newl.group(2)
       table.features = newl.group(3)
       table_list.append(table)
 
       if train:
          #create a class list
          map_list.total += 1
          #map_list.counts[table.cls] = map_list.counts.get(table.cls,0) + 1
          map_list.index[table.cls] = 1

          # count number of features 
          for t,c in f_list:
              TERMS.add(t)

   if train:
      return table_list,map_list
   else:
      return table_list

def call_mallet(dir):

   null = '/dev/null'
   if not os.path.exists(null):
     os.makedirs(null)

   #data preparation
   file = dir + 'train'
   trainvect = dir + 'train.vectors'
   command = 'info2vectors --input ' + file + ' --output ' + trainvect
   subprocess.call(command,shell=True)

   file = dir + 'test'
   testvect = dir + 'test.vectors'
   command  = 'info2vectors --use-pipe-from ' +  trainvect + ' --input ' + file + ' --output ' + testvect + ' >' + null + ' 2>&1'
   subprocess.call(command,shell=True)

   #classify train data
   stdout = dir + 'stdout'
   stderr = dir + 'stderr'
   command = 'vectors2classify --training-file ' + trainvect + ' --testing-file ' + testvect + ' --trainer MaxEnt --report test:raw >' + stdout + ' 2>' + null 
   subprocess.call(command,shell=True)

#calculate probability
def classify(train_list,test_list,parent_dir):

   index_list = {}

   # initialize matrix
   matrix = output.Matrix(map_list.index.keys())

   for i,c in enumerate(map_list.index.keys()):

       subdir = str(i+1) + '-vs-all/' 
       dir = parent_dir + subdir
       #check if sub directory already exists 
       if not os.path.exists(dir):
          os.makedirs(dir) 
       
       train = open(dir + 'train','w')
       index_list[i+1] = c
       mapf.write("%s %d\n" % (c,i+1))

       for t in train_list:
          if re.search(c,t.cls):
             gold_class = 1
          else:
             gold_class = -1
          train.write("%s %d %s\n" % (t.instance,gold_class,t.features))
       train.close()

       test = open(dir + 'test','w')
       for t in test_list:
          if re.search(c,t.cls):
             gold_class = 1
          else:
             gold_class = -1
          test.write("%s %d %s\n" % (t.instance,gold_class,t.features))
       test.close()

       #run train.txt
       call_mallet(dir)
       
       #create sys_output from test.stdout
       temp = open(dir + 'stdout','r')
       sys = open(dir + 'sys_output','w')
       for l in temp.readlines():
           m = re.match('^(\S+) (\-?\d) (\-?\d):(\S+) (\-?\d):(\S+)',l)
           if m:
              sys.write("%s %s %s %s %s %s\n" % \
              (m.group(1),m.group(2),m.group(3),m.group(4),m.group(5),m.group(6)))           
              #store test probability into each table
              for t in test_list: 
                 if t.instance == m.group(1):   
                    if m.group(3) != '-1': 
                       prob = m.group(4)
                    else:
                       prob = m.group(6)
                    t.probs[i+1] = prob 
       temp.close()
       sys.close()
 
   #assign class with highest probability
   for t in test_list: 
       final = sorted(t.probs.items(),key=lambda x:float(x[1]),reverse=True)   
       index = final[0][0]
       sys_class = index_list[index] 
       matrix.set_value(t.cls,sys_class,1) 
       #output
       final_sys.write("%s %s" %(t.instance,t.cls))
       for cls,prob in final:
          final_sys.write(" %s %s" %(index_list[cls],prob))
       final_sys.write('\n')
 
   return matrix


###################
#main function

#open files
trainf = open(sys.argv[1],'r')
testf = open(sys.argv[2],'r')
outdir = sys.argv[3]
mapf = open(outdir + 'class_map','w')
final_sys = open(outdir + 'final_sys_output','w')

#sort data
TRAIN = 1
train_table,map_list = sort_data(trainf,TRAIN)
TRAIN = 0 
test_table = sort_data(testf,TRAIN)

#classify
matrix=classify(train_table,test_table,outdir)

#output acc file header
sys.stdout.write('class_num=' + str(len(map_list.index)) + \
                 ' feat_num=' + str(len(TERMS)) + '\n')
# output result
doc_count = len(test_table)
matrix.output_acc(sys.argv[2],doc_count,map_list.index)

#close file handlers
trainf.close()
testf.close()
mapf.close()
final_sys.close()
