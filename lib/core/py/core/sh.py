from __future__ import with_statement
import os
import os.path
import fnmatch
import itertools
import urllib2

##    cat/tac           - read lines of text from a file
##    head/tail         - read first or last lines of text from a file
##    cp/mv/rm          - copy/move/remove a file
##    ls                - list files and directories in directory
##    find              - list files in directory and subdirectores
##    test              - test file for conditions
##    todos/fromdos     - convert newlines unix <-> dos
##    tomac/frommac     - convert newlines unix <-> mac
##    mkdir/rmdir       - create/remove directories
##    basename/dirname  - split dirname/filename
##    extname			- split extension
##    wget              - download
##    run               - run command

# done: 
# cat/tac
# ls
# find
# head
# tail
# wget
# run

def as_text(name):
    def as_text_dec(func):
        def as_text_func(*a, **k):
            for thing in func(*a, **k):
                print thing
        as_text_func.__doc__ = func.__doc__
        as_text_func.__name__ = name
        globals()[name] = as_text_func
        return func 
    return as_text_dec

def as_list(name):
    def as_list_dec(func):
        def as_list_func(*a, **k):
            return list(func(*a, **k))
        as_list_func.__name__ = name
        as_list_func.__doc__ = func.__doc__
        globals()[name] = as_list_func
        return func
    return as_list_dec

@as_text('cat')
@as_list('catl')
def catf(*filenames):
    "cat(*filenames) -> list of str containing lines from files"
    for filename in filenames:
        with open(filename,'r') as f:
            for line in f:
                yield line[:-1] 

@as_text('tac')
@as_list('tacl')
def tacf(*semanelif):
    for emanelif in semanelif[::-1]:
        with open(emanelif,'r') as f:
            for enil in f.readlines()[::-1]:
                yield enil[:-1]
                
@as_text('ls')
@as_list('lsl')
def lsf(d, pattern=None, recurse=False, dirs=True):
    for fn in sorted(os.listdir(d)):
        fn = (d + '/').replace('//', '/') + fn
        if recurse and os.path.isdir(fn):
            for sfn in lsf(fn, pattern, recurse, dirs):
                yield sfn
        fnmatches = (not pattern) or fnmatch.fnmatch(fn, pattern)
        showdir = dirs or not os.path.isdir(fn)
        if fnmatches and showdir:
            yield fn

@as_text('find')
@as_list('findl')
def findf(d, pattern=None):
    return lsf(d, pattern, recurse=True, dirs=False)

@as_text('head')
@as_list('headl')
def headf(filename, lines=10):
    for line in catf(filename):
        yield line
        lines -= 1
        if not lines:
            break    

@as_text('tail')
@as_list('taill')
def tailf(filename, lines=10):
    for line in catl(filename)[-lines:]:
        yield line

def wgetf(url):
    return urllib2.urlopen(url)

def wget(url, out):
    with open(out, 'wb') as outf:
        inf = wgetf(url)
        outf.write(inf.read())

def test(condition, filename1, filename2=None):
    if condition == 'f':
        try:
            os.stat(filename1)
            return True
        except:
            return False
    else:
        raise NotImplemented('condition ' + repr(condition))

def run(cmd, stdin=None):
	import subprocess
	if stdin:
		p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		p.stdin.write(stdin)
		p.stdin.close()
	else:
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)	
	return p.stdout.read()
	
del as_text
del as_list

if __name__ == '__main__':
    #cat('sh2.py')
    #print catl('sh2.py')
    #tac('sh2.py')
    #cat('sh2.py, 'mp3.ini')

    #ls('.')
    #ls('.','*.ini')

    #find('.','*.jpg')

    #head('sh2.py', 1)
    #tail('sh2.py', 1)


    pass
