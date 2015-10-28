#!/bin/python

import collections
import fileinput
import os
import re
import sys

###############################################################################
# This script takes the output from a compilation using an existing legacy
# compiler such as Sun's f90 and uses its warnings as a list of places to fix
# the source code. It will then attempt to convert it to a more
# standard-compliant form, with the aim of making it acceptable to gfortran.

# Original code by Mark Doffman, maintained by Jim MacArthur.


def split_fortran_line_at_72(line):
    # The first string is in position 7 and must only be a single character
    # when inserted.
    # The second string is at position 73 and will be ignored by the compiler
    # if present.
    single_char_line =  "     +%s"
    single_char_line_with_over =  "     +%s" + ' '*65 + "%s"

    keep = line[:72]
    last = line[72]

    print keep
    if len(line) > 73:
        over = line[73:]
        print single_char_line_with_over % (last, over)
    else:
        print single_char_line % (last)

def main():
    typesAsPrints = collections.defaultdict(list)
    ansiRegex = re.compile('^\"(.*)\".*?Line = (\d*).*?(\(.*?ANSI_TYPE_AS_PRINT.*?\))')

    for line in sys.stdin:
        m = ansire.search(line)
        if m:
            print "Adding usage: %s to %s"%(m.group(1), m.group(2))
            typesAsPrints[m.group(1)].append(int(m.group(2)))

    typere = re.compile('type', re.IGNORECASE)

    for filename, lines in typesAsPrints.items():
        if not os.path.exists(filename):
            print "Warning: file %s does not exist"%filename
            continue
        print "Processing file %s, line %s"%(filename, lines)
        for line in fileinput.input(os.path.join(filename), inplace=True):
            if fileinput.filelineno() in lines:
                subst_line = typere.sub('print', line.rstrip(), count=1)
                if len(subst_line) > 72:
                    split_fortran_line_at_72(subst_line)
                else:
                    print subst_line
            else:
                print line,
