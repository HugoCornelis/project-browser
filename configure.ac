dnl
dnl Neurospaces project browser: define projects, and explore results.
dnl
dnl $Id: configure.in 1.27 Sat, 21 Apr 2007 21:39:05 -0500 hugo $
dnl

dnl //////////////////////////////////////////////////////////////////////////
dnl
dnl Neurospaces project browser: define projects, and explore results.
dnl
dnl Copyright (C) 2007-2008 Hugo Cornelis, hugo.cornelis@gmail.com
dnl
dnl //////////////////////////////////////////////////////////////////////////

# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)

# $Format: "AC_INIT(${package}, ${label}, ${email})"$
AC_INIT(project-browser, python-2, hugo.cornelis@gmail.com)

AC_CONFIG_SRCDIR([neurospaces_output_browser/output.cgi])

# $Format: "AM_INIT_AUTOMAKE(${package}, ${label})"$
AM_INIT_AUTOMAKE(project-browser, python-2)

PERL_MODULES=`(cd perl && find . -name "*.pm" -printf "%p ")`
AC_SUBST(PERL_MODULES)

# Checks for programs.

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

# find all usermin modules

USERMIN_MODULES=`find {Sesa,neurospaces_*,images} -printf "%p "`

AC_SUBST(USERMIN_MODULES)

USERMIN_DIR=/usr/share/usermin

AC_SUBST(USERMIN_DIR)


AC_CONFIG_FILES([Makefile
		 perl/Makefile
		 tests/Makefile
		])

AC_OUTPUT

