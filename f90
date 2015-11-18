#!/usr/bin/python

import os
import sys

gfortranBinary = "/home/jmacarthur7/gccinstall/bin/gfortran"

def main():
    if not os.path.exists(gfortranBinary):
        print("The gfortran binary %s (hardcoded in this program)"
              " does not exist." % gfortranBinary)
        exit(1)

    args = sys.argv[1:]
    gccArgs = [ '-foracle-support -foracle-support-experimental' ]
    while len(args)>0:
        arg = args.pop(0)
        if arg.startswith("-erroff="):
            pass # Ignore this
        elif arg == "-u":
            gccArgs.append("-fimplicit-none")
        elif arg == "-xrecursive":
            gccArgs.append("-frecursive")
        elif arg == "-pic":
            gccArgs.append("-fpic")
        elif arg == "-ansi":
            pass # Ignore it
        elif arg.startswith("-errtags"): pass
        elif arg.startswith("-xarch="): pass
        elif arg == "-xhasc=no": pass
        elif arg == "-f77": pass
        elif arg == "-ftrap=%none": pass
        elif arg == "-f77=no%backslash": pass
        elif arg == "-aligncommon=1":
            gccArgs.append("-fno-align-commons")
        else:
            gccArgs.append(arg)
    command = [ gfortranBinary ]
    command.extend(gccArgs)
    os.execv(gfortranBinary, command)

if __name__=="__main__": main()
