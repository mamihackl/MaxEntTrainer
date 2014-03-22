#!/opt/python-2.6/bin/python2.6
# Mami Hackl and Nat Byington
# LING 572 HW7 Q2 All-Pair
# Classify test data using Mallet with only two classes at a time.
# PLEASE NOTE THAT THIS PROGRAM IS HARD-CODED FOR THREE CLASSES:
# 1. talk.politics.guns 2. talk.politics.mideast 3. talk.politics.misc
# Args: training, test, output_dir > acc 

import sys
import re
import os
import subprocess

### Functions

def create_pair_file(orig_file, new_file, class1, class2, test):
    ''' Create a new training or test file out of the original file using
        a pair of class names. class1 gets assigned '1' and class2 gets
        assigned '-1'. The bool 'test' indicates whether or not orig_file
        is a test file.'''
    for line in orig_file.readlines():
        instance, classname = re.match(r'^([\S]+) ([\S]+) ', line).group(1,2)
        if instance not in FINAL_RESULTS:
            FINAL_RESULTS[instance] = [classname, False, False, False]
        if classname == class1:
            new_file.write(re.sub(' '+classname, ' 1', line))
        elif classname == class2:
            new_file.write(re.sub(' '+classname, ' -1', line))
        elif test:
            # only writes a 0 instance if this is a test file; ignored otherwise
            new_file.write(re.sub(' '+classname, ' 0', line))
            
def classify_pair(sub_dir, index_slot, orig_train, orig_test, c1, c2):
    ''' Use mallet to classify using a pair of classes. Given the subdirectory
        and the appropriate index slot to use in FINAL_RESULTS. '''
    old_train = open(orig_train)
    old_test = open(orig_test)
    os.mkdir(sub_dir)
    os.chdir(sub_dir)
    new_train = open('train', 'w')
    new_test = open('test', 'w')
    create_pair_file(old_train, new_train, c1, c2, False)
    create_pair_file(old_test, new_test, c1, c2, True)
    old_train.close()
    old_test.close()
    new_train.close()
    new_test.close()
    subprocess.call('info2vectors --input train --output train.vectors', 
                    shell=True, stderr=NULL)
    subprocess.call('info2vectors --input test --output test.vectors --use-pipe-from train.vectors',
                    shell=True, stderr=NULL)
    subprocess.call('vectors2classify --training-file train.vectors --testing-file test.vectors --trainer MaxEnt --report test:raw > sys_output',
                    shell=True, stderr=NULL)
    # process sys out file to get data for final output
    # getting the c1 and c2 probs in the correct order (c1,c2) is important!
    sys_out = open('sys_output')
    for line in sys_out.readlines():
        if re.match(r'^../20_news', line):
            inst,cprobs = re.match(r'^([\S]+) [\S]+ ([\S]+:[\S]+ [\S]+:[\S]+ [\S]+:[\S]+)',
                                   line).group(1,2)
            class_probs = []
            for i in cprobs.split():
                x = i.split(':')
                y = (int(x[0]), float(x[1]))
                class_probs.append(y)
            class_probs.sort(reverse=True) # makes '1' first element, '-1' last
            FINAL_RESULTS[inst][index_slot] = (class_probs[0][1], class_probs[2][1]) # tuple with probs for c1,c2
    sys_out.close()
    os.chdir('..') # go back to parent directory
    
### Main
# Get files and values from arguments.
train = sys.argv[1] # unopened
test = sys.argv[2] # unopened
output_dir = sys.argv[3]

# Create required subdirectories and files for processing.
os.chdir(output_dir) # change working directory to output directory
sub1 = '1-vs-2'
sub2 = '1-vs-3'
sub3 = '2-vs-3'
cl1 = 'talk.politics.guns'
cl2 = 'talk.politics.mideast'
cl3 = 'talk.politics.misc'
class_map = open('class_map', 'w')
final_out = open('final_sys_output', 'w')
NULL = open(os.devnull, 'w')
FINAL_RESULTS = {} # dictionary using instance name as key
class_map.write('talk.politics.guns\t1\ntalk.politics.mideast\t2\ntalk.politics.misc\t3\n')

# Call classifying functions
classify_pair(sub1, 1, train, test, cl1, cl2)
classify_pair(sub2, 2, train, test, cl1, cl3)
classify_pair(sub3, 3, train, test, cl2, cl3)

# Output final_sys_output and acc data
classes = [cl1, cl2, cl3]
MATRIX = dict( [(x, {}) for x in classes] )
for c in classes:
    for c2 in classes:
        MATRIX[c][c2] = 0
v_count = 0
testf = open(test)
for line in testf.readlines():
    v_count += 1
    instance, true_class = re.match(r'^([\S]+) ([\S]+) ', line).group(1,2)
    c1wins, c2wins, c3wins = 0,0,0
    output = [instance, true_class]
    #tally wins
    if FINAL_RESULTS[instance][1]:
        if (FINAL_RESULTS[instance][1][0] >= FINAL_RESULTS[instance][1][1]):
            c1wins += 1
        else:
            c2wins += 1
    if FINAL_RESULTS[instance][2]:
        if (FINAL_RESULTS[instance][2][0] >= FINAL_RESULTS[instance][2][1]):
            c1wins += 1
        else:
            c3wins += 1
    if FINAL_RESULTS[instance][3]:
        if (FINAL_RESULTS[instance][3][0] >= FINAL_RESULTS[instance][3][1]):
            c2wins += 1
        else:
            c3wins += 1
    results = [(c1wins, cl1, 'c1='), (c2wins, cl2, 'c2='), (c3wins, cl3,'c3=')]
    results.sort(reverse=True)
    # build output
    sys_class = results[0][1]
    MATRIX[true_class][sys_class] += 1
    p12 = str(FINAL_RESULTS[instance][1][0])
    p13 = str(FINAL_RESULTS[instance][2][0])
    p23 = str(FINAL_RESULTS[instance][3][0])
    r1 = results[0][2] + str(results[0][0]) # c1=n1 stuff
    r2 = results[1][2] + str(results[1][0])
    r3 = results[2][2] + str(results[2][0])
    output.extend([sys_class,'1:2',p12,'1:3',p13,'2:3',p23,r1,r2,r3,'\n'])
    final_out.write(' '.join(output))
          
# Output accuracy results using MATRIX data
sys.stdout.write('class_num=' + str(len(classes)) + '\n')
correct = 0.0
print 'Confusion matrix:'
print 'row is the truth, column is the system output'
print ''
sys.stdout.write('\t\t')
for c in classes:
    sys.stdout.write(' ' + c)
    correct += MATRIX[c][c]
sys.stdout.write('\n')
for c in classes:
    sys.stdout.write(c)
    for c2 in classes:
        sys.stdout.write(' ' + str(MATRIX[c][c2]))
    sys.stdout.write('\n')
print ''
print 'Accuracy: ' + str(correct / float(v_count))
print ''
    

