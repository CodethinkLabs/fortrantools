# fortrantools

These are tools to help you use old or proprietary Fortran code with gfortran. They're intended to be used together with the gcc extensions in CodethinkLab's gcc branch. 

By a combination of source code preprocessing and modifications to gfortran, we can support several features otherwise only present in proprietary compilers.

There are three tools provided in this repository:

* type-to-print.py is a script to find and replace instances of TYPE where the keyword is used as a synonym for PRINT, as in:

    TYPE *, "Hello world".

* converter.py performs various other fixes, such as removing IMPLICIT NONE statements and joining continued include lines.

* f90 is a shim which is intended to be called instead of the actual 'f90' executable. It translates some command-line options
  and then invokes gfortran.

# How to use these scripts

There are two main scripts used for conversion, type-to-print.py and convert.py. These are invoked differently so haven't been combined into one tool, yet.

## type-to-print

type-to-print requires that you have access to the original compiler, or at least have a build log containing warnings about TYPE statements used as PRINT statements.
This log should be fed into type-as-print:

    ./type-as-print.py < warning-log

The script will locate examples of the warning and extract the filename, and use these to correct the source file. The script is dependent on the output format of the Oracle f90 compiler; other compilers may vary.

## convert

convert.py works without any input and converts any .f and .inc files found in the current directory, so can simply be run as is:

    ./convert.py

## f90

Finally, "f90" should be placed on your path somewhere before the actual Fortran compiler it replaces. You will need to alter the path to gfortran which is hardcoded in f90. If you've installed a custom gfortran via a package manager, this will just be the output of 'which gfortran'. You may also need to alter the command-line translations inside it, depending on which Fortran compiler your build system expects to be using.

# GFortran branches

There are two branches on github which can be considered stable, based on GCC 4.8 and GCC 5.2:

* jmac/legacy-support-5_2-B (https://github.com/CodethinkLabs/gcc/tree/jmac/legacy-support-5_2-B)
* jmac/legacy-support-4_8-L (https://github.com/CodethinkLabs/gcc/tree/jmac/legacy-support-4_8-L)

These can be built and used like normal GCC. The extra features added are /mostly/ enabled with "-fstd=extra-legacy".

# Legacy features which we can fix by preprocessing source

## TYPE-to-PRINT conversion

This would be a trivial replacement if it weren't for the fact that this pushes some lines over the 72 character limit. If that happens, the remainder of the line is pasted on the next line, with a continuation character. To maintain correctness in free-form Fortran, the characters after column 72 are printed on the first line anyway, and the comment character ('!') is used as the continuation character.

## IMPLICIT NONE

gfortran requires IMPLICIT NONE statements to be at the beginning of a block, but other compilers can accept it anywhere inside a block. Hence, Fortran code exists with IMPLICIT NONE after statements. converter.py contains code to move these statements upwards until it finds what it considers a block-starting statement such as FUNCTION. However, it fails when INCLUDE statements are used inside blocks. Since the included code may end the block and start a new one, it is not correct to move an IMPLICIT NONE statement above an INCLUDE statement; nor is it correct to move it into the included code, since the same code may be included by another file without the IMPLICIT NONE.

At the moment, converter.py simply removes IMPLICIT NONE statements, the reasoning being that this will never affect the functionality of a program, it will just hide a potential warning.

## Continued include lines

An 'include' statement which is continued over several lines is prohibited by most Fortran standards, but this still occurs. Because the behaviour isn't written in any standard, the behaviour is ambiguous. The continuation could either extend the include line itself, or the last line in the included file. We choose to interpret it as the include line. A future refinement would be to look for nonterminated quotes.

converter.py will join include statements followed by a continuation line into one line. Note that this will often push the line over 72 characters (otherwise there would have been no reason to use the continuation). The 'legacy-support' branch of gfortran is altered to accept include statements longer than 72 characters. Using this transformation may make your code incompatible with your existing Fortran compiler.

# Legacy features implemented in the compiler

* STRUCTURE, RECORD and UNION support has been backported from GCC 6. These need be enabled -fdec-structure.
* .xor. is allowed as an alias for .neqv.
* Array references for multi-dimensional arrays can be omitted. For example, an array declared as

    INTEGER chrbrd(8,8)

... can be used as "chsbrd(3)". This still returns a single INTEGER; the index for missing dimensions is always the lowest value for that dimension in this case.

* Variables can be declared twice, as long as the data types are the same.
* Subroutines and functions can be declared twice, even with different return types or argument types; the most recent declaration will be used.
* Include lines which are longer than 72 characters are allowed.
* You can specify a 'kind' for each variable declared in one statment. The following will now be accepted:

    INTEGER*4 x*2, y*8

* Basic support for old-style initializers inside derived types and structures.

    LOGICAL*1      NIL      /0/

Only single-value expressions are supported at the moment.


## Relaxing of type conversion rules
* Logicals can be automatically converted to integers in arithmetic operations.
* Characters (hollerith constants or strings) can be converted to integers automatically inside a DATA statement.
* Characters can be assigned to integers.
* Calls to intrinsic functions, passing smaller data types than expected. With -std=extra-legacy, these values will be converted to larger types.
* Non-logical expressions are allowed in the clause of IF statements.
* Integers can be convered to logicals and used by logical operators.
* Hollerith and character variables can be compared with the usual character-to-character operators.

## Others

* Character-to-integer conversions will be padded with spaces instead of zeros if the string isn't long enough for the type. This is either 'undefined' or 'processor depenedent' depending on which standard you read; padding with zeros matches the observed behaviour of the Oracle compiler.


* You can mix string length and array specification in CHARACTER declarations

  TODO: An example would be useful here

* Blank format items are allowed in format strings

  TODO: An example and more explanation would be useful here.

* Non-integer expressions are allowed as substring indexes, and will be converted to them

  TODO: An example would be useful here

* More than one character can be passed to ICHAR. Only the first one will be used.

