#!/usr/bin/env python

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
# It will find all the files in the current directory (CWD) with an extension of
# .f or .inc and attempt to process them.

# There are four operations defined, of which only two are used

# 1) Rewriting old style initializers as new ones
# 2) Reordering of IMPLICIT NONE statements
# 3) Removal of IMPLICIT NONE statements
# 4) Joining of continued include lines into long include lines.

# Of these, only 3) and 4) are used at the moment. See the README file for the
# reasons behind this.

joinLines = False

def isComment(line):
    return len(line)>0 and line[0] in commentCharacters

def isContinuation(line):
    return len(line)>5 and line[5] not in [' ','0'] and not isComment(line)

def fixOldStyleInitializers(lines):
    initRegex = re.compile('(?P<type>INTEGER|LOGICAL|CHARACTER)(?P<kind>\*\(?\d+\)?)?\s+(?P<ident>\S+)\s*\/(?P<value>\S+)\/(?P<tail>\s*,.*$)')
    oldDeclarationRegex = re.compile('(?P<ident>\S+)\s*\/(?P<value>\S+)\/')
    newLines = []
    for lineno in range(0,len(lines)):
        line = lines[lineno]
        m = initRegex.search(line.rstrip())
        if m:
            print "Matched old-style initializer line"
            newLine = "      %s%s :: %s = %s"%(m.group('type'), m.group('kind') or "", m.group('ident'), m.group('value'))

            # Check for further declarations
            declarations = m.group('tail').split(",")
            newDeclarations = []
            for d in declarations:
                print "checking subsequent declaration %s"%d

                if oldDeclarationRegex.search(d):
                    newDeclarations.append("%s = %s"%(m.group('ident'), m.group('value')))
                else:
                    newDeclarations.append(d)
            newLines.append(newLine + ",".join(newDeclarations) + "\n")
        else:
            newLines.append(line)
    return newLines

def fixImplicitStatements(lines):
    implicitRegex = re.compile('^\s+IMPLICIT ', re.IGNORECASE)
    programUnitStartRegex = re.compile('\s+(PROGRAM|SUBROUTINE|FUNCTION|BLOCK|INCLUDE)\s+', re.IGNORECASE)
    insertPoint = 0
    print "Reordering IMPLICIT statements..."
    for lineno in range(0,len(lines)):
        l = lines[lineno]
        if implicitRegex.search(l.rstrip()):
            lines.pop(lineno)
            lines.insert(insertPoint, l) # Inserts before insertPoint
            print "Removed line from %d and inserted it at %d"%(lineno,insertPoint)
        elif programUnitStartRegex.search(l.rstrip()):
            insertPoint = lineno+1
            # Advance until we are not before a continuation line.
            while insertPoint < len(lines) and isContinuation(lines[insertPoint]):
                print "Winding forward as %d is a continuation line."%(insertPoint)
                insertPoint += 1
            print "Insert point is now %d"%insertPoint
    return lines

def removeImplicitStatements(lines):
    implicitRegex = re.compile('^\s+IMPLICIT NONE', re.IGNORECASE)
    print "Removing IMPLICIT NONE statements..."
    newlines = []
    lineno = 1
    for l in lines:
        if not implicitRegex.search(l.rstrip()):
            newlines.append(l)
        else:
            print "Removed IMPLICIT NONE line from %d"%lineno
        lineno += 1
    return newlines

def replaceIncludeWithDirective(includeLine):
    includeRegex = re.compile('^\s+INCLUDE\s*\'(\S+)\'$', re.IGNORECASE)
    m = includeRegex.search(includeLine)
    if m:
        includeLine = "#include \"%s\"\n" % m.group(1)
    return includeLine

def joinIncludes(lines):
    # Look for include statements that have no filename
    includeRegex = re.compile('^\s+INCLUDE\s*$', re.IGNORECASE)
    for lineno in range(0,len(lines)):
        if lineno >= len(lines): break
        l = lines[lineno]
        if includeRegex.search(l.rstrip()):
            print "Detected include on line %d"%lineno
            while lineno < len(lines)-1 and isContinuation(lines[lineno+1]):
                print "%d is a continuation"%(lineno+1)
                c = lines.pop(lineno+1)[6:]
                l = l.rstrip() + c
            l = l.rstrip()
            if len(l) > 72:
                lines[lineno] = replaceIncludeWithDirective(l)
            else:
                lines[lineno] = l+"\n"
    return lines

def removeDebugComments(lines):
    debugCommentRegex = re.compile('^D')
    print "Removing debug ('D') comment lines..."
    newlines = []
    lineno = 1
    for l in lines:
        if not debugCommentRegex.search(l.rstrip()):
            newlines.append(l)
        else:
            print "Removed debug comment line from %d"%lineno
            lineno += 1
    return newlines

def convertXorToNeqv(lines):
    xorRegex = re.compile('\.xor\.')
    newlines = []
    lineno = 1
    for l in lines:
        newlines.append(re.sub(xorRegex, '.neqv.', l))
    return newlines

def fixFortran(filename):
    allLines = []
    print "Processing %s"%filename
    f = open(os.path.join(filename), 'rt')
    allLines = f.readlines()
    f.close()
    print "%d lines read from file"%len(allLines)
    if joinLines:
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

    # Process old-style initializers
    #allLines = fixOldStyleInitializers(allLines)
    allLines = removeImplicitStatements(allLines)
    allLines = joinIncludes(allLines)
    allLines = removeDebugComments(allLines)
    allLines = convertXorToNeqv(allLines)

    f = open(os.path.join(filename), 'wt')
    for l in allLines:
        if joinLines:
            for sl in split_fortran_line_at_72(l):
                f.write(sl)
        else:
            f.write(l)
    f.close()

def getFortranFiles():
    path = "."
    onlyfiles = [ f for f in listdir(path) if isfile(join(path,f)) and (f.endswith('.f') or f.endswith('.inc')) ]
    return onlyfiles

def main():
    # New method for processing files:
    for f in getFortranFiles(): fixFortran(f)

if __name__=="__main__": main()
