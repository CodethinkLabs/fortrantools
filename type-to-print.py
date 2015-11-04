#!/bin/python

import collections
import fileinput
import os
import re
import sys
from os import listdir
from os.path import isfile, join
from fortranUtils import split_fortran_line_at_72

###############################################################################
# This script takes the output from a compilation using an existing legacy
# compiler such as Sun's f90 and uses its warnings as a list of places to fix
# the source code. It will then attempt to convert it to a more
# standard-compliant form, with the aim of making it acceptable to gfortran.

# Original code by Mark Doffman, maintained by Jim MacArthur.

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

if __name__=="__main__": main()
