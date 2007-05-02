##
## Neurospacesweb: visualize neuronal simulations and their results.
##
## $Id: configure.in 1.27 Sat, 21 Apr 2007 21:39:05 -0500 hugo $
##

##############################################################################
##'
##' Neurospacesweb: visualize neuronal simulations and their results.
##'
##' Copyright (C) 2007 Hugo Cornelis, hugo.cornelis@gmail.com
##'
##############################################################################


dist_bin_SCRIPTS =

# no tests yet!
# the perl library is copied overhere.
#
# The variable EXTRA_DIST could also be used here.

dist-hook:
	find $(distdir) -name _Inline -exec chmod u+w -R \{\} \;
	$(RM) -fr `find $(distdir) -name _Inline`
	cp $(srcdir)/license.txt $(distdir)
	cp -R $(srcdir)/docs $(distdir)
	cp -R {Sesa,neurospaces_*,images} $(distdir)
#	test -d $(distdir)/tests || mkdir $(distdir)/tests
#	test -d $(distdir)/tests/specifications || mkdir $(distdir)/tests/specifications
#	cp -R $(srcdir)/tests/run $(distdir)/tests/run
#	cp -R $(srcdir)/tests/tests_2_html $(distdir)/tests/tests_2_html
#	cp -R $(srcdir)/tests/specifications $(distdir)/tests
##	cp -R $(srcdir)/tests/code/tests.config $(distdir)/tests/code/tests.config
#	cp -R $(srcdir)/tests/tests.config $(distdir)/tests/tests.config
#	cp -R $(srcdir)/tests.config $(distdir)
#	cp -R $(srcdir)/tests/perl $(distdir)/tests
#	cp -R $(srcdir)/perl $(distdir)

html-upload-prepare:
	rm -fr html/htdocs/neurospaces_project/neurospacesweb/
	mkdir --parents html/htdocs/neurospaces_project/neurospacesweb
	mkdir --parents html/htdocs/neurospaces_project/neurospacesweb/html_source
	tar cfh - tests/html | ( cd html/htdocs/neurospaces_project/neurospacesweb && tar vxf - )

html-upload: html-upload-prepare
	scp -pr html/htdocs/* hcornelis@shell.sourceforge.net:/home/groups/n/ne/neurospaces/htdocs/

#t make this one configurable

usermindir = /usr/share/usermin

install-exec-hook:
	cp -R {Sesa,neurospaces_*,images} $(usermindir)

#EXTRA_SCRIPTS = `find {Sesa,neurospaces_*,images} -printf "%p "`

#`find {Sesa,neurospaces_*,images} -printf "%p "`
#@USERMIN_MODULES@
#usermindir = /usr/share/usermin

#usermin_HEADERS = @USERMIN_MODULES@
