#!/bin/python

import collections
import fileinput
import os
import re
import sys
from os import listdir
from os.path import isfile, join
from fortranUtils import split_fortran_line_at_72, commentCharacters

###############################################################################
# This code attempts to fix various pieces of legacy Fortran which will not
# otherwise compile with gfortran.

def isComment(line):
    return len(line)>0 and line[0] in commentCharacters

def isContinuation(line):
    return len(line)>5 and line[5] != ' ' and not isComment(line)

def fixFortran(filename):
    allLines = []
    print "Processing %s"%filename
    f = open(os.path.join(filename), 'rt')
    allLines = f.readlines()
    f.close()
    print "%d lines read from file"%len(allLines)
    # Rejoin all lines.
    for lineno in range(0,len(allLines)):
        allLines[lineno] = allLines[lineno][:72]

    for lineno in range(0,len(allLines)):
        if lineno >= len(allLines): break
        if isComment(allLines[lineno]):
                print "Skipping comment line %d"%lineno
                continue
        while lineno < len(allLines) and isContinuation(allLines[lineno]):
            l = allLines.pop(lineno)
            allLines[lineno-1] = allLines[lineno-1].rstrip() + l[6:72]
            print "Removed line %d and added it to the end of the preceding line"%(lineno)
    print "%d lines after rejoining"%len(allLines)

    # Now do processing
    initRegex = re.compile('(?P<type>INTEGER|LOGICAL|CHARACTER)(?P<kind>\*\(?\d+\)?)?\s+(?P<ident>\S+)\s*\/(?P<value>\S+)\/(?P<tail>\s*,.*$)')
    lines = []
    for lineno in range(0,len(allLines)):
        line = allLines[lineno]
        m = initRegex.search(line.rstrip())
        if m:
            print "Matched old-style initializer line"
            newLine = "      %s%s :: %s = %s%s\n"%(m.group('type'), m.group('kind') or "", m.group('ident'), m.group('value'), m.group('tail'))
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
    # New method for processing files:
    for f in getFortranFiles(): fixFortran(f)

if __name__=="__main__": main()
