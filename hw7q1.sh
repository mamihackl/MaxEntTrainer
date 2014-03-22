#!/bin/bash
#Ling572 HW7q1: 1-vs-all
#Nat Byington
#Mami Hackl 
command='./q1.sh'
path='/opt/dropbox/09-10/572/hw7/examples/'
trainf='train.txt'
testf='test.txt'
outdir='q1-res/'
accf='acc_file'
testdir='test/'
traindir='train/'

#create directlry if it doesn't exist already
if [ ! -d "$outdir" ];then
 mkdir -p $outdir
fi

parentdir=$outdir$testdir
if [ ! -d "$parentdir" ];then
 mkdir -p $parentdir
fi

$command $path$trainf $path$testf $parentdir >$parentdir$accf 

parentdir=$outdir$traindir
if [ ! -d "$parentdir" ];then
 mkdir -p $parentdir
fi
$command $path$trainf $path$trainf $parentdir >$parentdir$accf 
