# fortrantools

These are tools to help you use old or proprietary Fortran code with gfortran. They're intended to be used together with the gcc extensions in CodethinkLab's gcc branch at https://github.com/CodethinkLabs/gcc/tree/jmac/legacy-support-4_8-L.

There are three tools provided:

* type-to-print.py is a script to find and replace instances of TYPE where the keyword is used as a synonym for PRINT, as in:

    TYPE *, "Hello world".

* converter.py performs various fixes, such as removing IMPLICIT NONE statements and joining continued include lines.

* f90 is a shim which is intended to be called instead of the actual 'f90' executable. It translates some command-line options
  and then invokes gfortran.

# How to use these scripts

There are two main scripts used for conversion, type-to-print.py and convert.py. These are invoked differently so haven't been combined into one tool, yet.

type-to-print requires that you have a build log containing warnings about TYPE statements used as PRINT statements. This log should be fed into type-as-print:

    ./type-as-print.py < warning-log

The script will locate examples of the warning and extract the filename, and use these to correct the source file.

convert.py works without any input and converts any .f and .inc files found in the current directory, so can simply be run as is:

    ./convert.py

Finally, "f90" should be placed on your path somewhere before the actual Fortran compiler it replaces. You will need to alter the path to gfortran which is hardcoded in f90. If you've installed a custom gfortran via a package manager, this will just be the output of 'which gfortran'. You may also need to alter the command-line translations inside it, depending on which Fortran compiler your build system expects to be using.

# TYPE-to-PRINT conversion

This would be a trivial replacement if it weren't for the fact that this pushes some lines over the 72 character limit. If that happens, the remainder of the line is pasted on the next line, with a continuation character. To maintain correctness in free-form Fortran, the characters after column 72 are printed on the first line anyway, and the comment character ('!') is used as the continuation character.

# IMPLICIT NONE

gfortran requires IMPLICIT NONE statements to be at the beginning of a block, but other compilers can accept it anywhere inside a block. Hence, Fortran code exists with IMPLICIT NONE after statements. converter.py contains code to move these statements upwards until it finds what it considers a block-starting statement such as FUNCTION. However, it fails when INCLUDE statements are used inside blocks. Since the included code may end the block and start a new one, it is not correct to move an IMPLICIT NONE statement above an INCLUDE statement; nor is it correct to move it into the included code, since the same code may be included by another file without the IMPLICIT NONE.

At the moment, converter.py simply removes IMPLICIT NONE statements, the reasoning being that this will never affect the functionality of a program, it will just hide a potential warning.

# Continued include lines

An 'include' statement which is continued over several lines is prohibited by most Fortran standards, but this still occurs. Because the behaviour isn't written in any standard, the behaviour is ambiguous. The continuation could either extend the include line itself, or the last line in the included file. We choose to interpret it as the include line. A future refinement would be to look for nonterminated quotes.

converter.py will join include statements followed by a continuation line into one line. Note that this will often push the line over 72 characters (otherwise there would have been no reason to use the continuation). The 'legacy-support' branch of gfortran is altered to accept include statements longer than 72 characters. Using this transformation may make your code incompatible with your existing Fortran compiler.


