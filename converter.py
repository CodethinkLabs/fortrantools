#!/bin/python

import collections
import fileinput
import os
import re
import sys
from os import listdir
from os.path import isfile, join

###############################################################################
# This script takes the output from a compilation using an existing legacy
# compiler such as Sun's f90 and uses its warnings as a list of places to fix
# the source code. It will then attempt to convert it to a more
# standard-compliant form, with the aim of making it acceptable to gfortran.

# Original code by Mark Doffman, maintained by Jim MacArthur.

def split_fortran_line_at_72(line):
    lines = [line]
    remain = line[72:]
    while len(remain)>66:
        lines.append("     +" + remain[:66] +"\n") 
        remain = remain[66:]
    if len(remain)>0:
        lines.append("     +" + remain)
    return lines

def fixFortran(filename):
    allLines = []
    print "Processing %s"%filename
    f = open(os.path.join(filename), 'rt')
    allLines = f.readlines()
    f.close()
    print "%d lines read from file"%len(allLines)
    # Rejoin all lines.
    for lineno in range(0,len(allLines)):
        if lineno >= len(allLines): break
        allLines[lineno] = allLines[lineno][:72]
        while len(allLines[lineno])>5 and allLines[lineno][5] != ' ':
            l = allLines.pop(lineno)
            allLines[lineno-1] = allLines[lineno-1].rstrip() + l[6:72]
            print "Removed line %d and added it to the end of the preceding line"%(lineno)
    print "%d lines after rejoining"%len(allLines)

    # Now do processing
    initRegex = re.compile('(?P<type>INTEGER|LOGICAL|CHARACTER)(?P<kind>\*\(?\d+\)?)?\s+(?P<ident>\S+)\s*\/(?P<value>\S+)\/')
    lines = []
    for lineno in range(0,len(allLines)):
        line = allLines[lineno]
        m = initRegex.search(line.rstrip())
        if m:
            print "Matched old-style initializer line"
            newLine = "      %s%s :: %s = %s\n"%(m.group('type'), m.group('kind'), m.group('ident'), m.group('value'))
            lines.append(newLine)
        else:
            lines.append(line)

    f = open(os.path.join(filename), 'wt')
    for l in lines:
        for sl in split_fortran_line_at_72(l):
            f.write(sl)
    f.close()

def getFortranFiles():
    path = "."
    onlyfiles = [ f for f in listdir(path) if isfile(join(path,f)) and (f.endswith('.f') or f.endswith('.inc')) ]
    return onlyfiles

def main():
    typesAsPrints = collections.defaultdict(list)
    ansiRegex = re.compile('^\"(.*)\".*?Line = (\d*).*?(\(.*?ANSI_TYPE_AS_PRINT.*?\))')

    for line in sys.stdin:
        m = ansiRegex.search(line)
        if m:
            print "Adding usage: %s to %s"%(m.group(1), m.group(2))
            typesAsPrints[m.group(1)].append(int(m.group(2)))

    typeRegex = re.compile('t\s*y\s*p\s*e', re.IGNORECASE)

    # The original method for processing files, as used by Mark to correct TYPE_AS_PRINT

    for filename, lines in typesAsPrints.items():
        if not os.path.exists(filename):
            print "Warning: file %s does not exist"%filename
            continue
        print "Processing file %s, line %s"%(filename, lines)
        for line in fileinput.input(os.path.join(filename), inplace=True):
            if fileinput.filelineno() in lines:
                subst_line = typeRegex.sub('print', line.rstrip(), count=1)
                for l in split_fortran_line_at_72(subst_line): print l,
            else:
                print line,


    # New method for processing files:
    for f in getFortranFiles(): fixFortran(f)

if __name__=="__main__": main()
