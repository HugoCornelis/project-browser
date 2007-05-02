dnl
dnl Neuroweb: visualize neuronal simulations and their results.
dnl
dnl $Id: configure.in 1.27 Sat, 21 Apr 2007 21:39:05 -0500 hugo $
dnl

dnl //////////////////////////////////////////////////////////////////////////
dnl
dnl Neuroweb: visualize neuronal simulations and their results.
dnl
dnl Copyright (C) 2007 Hugo Cornelis, hugo.cornelis@gmail.com
dnl
dnl //////////////////////////////////////////////////////////////////////////

# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)

# $Format: "AC_INIT(${package}, ${label}, ${email})"$
AC_INIT(neurospacesweb, nodist, hugo.cornelis@gmail.com)

AC_CONFIG_SRCDIR([neurospaces_output_browser/output.cgi])

# $Format: "AM_INIT_AUTOMAKE(${package}, ${label})"$
AM_INIT_AUTOMAKE(neurospacesweb, nodist)

# Checks for programs.

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

# find all usermin modules

USERMIN_MODULES=`find {Sesa,neurospaces_*,images} -printf "%p "`

AC_SUBST(USERMIN_MODULES)


AC_CONFIG_FILES([ Makefile ])

AC_OUTPUT

