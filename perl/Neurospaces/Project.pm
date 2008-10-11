#!/usr/bin/perl -w

##
## Neurospaces: a library which implements a global typed symbol table to
## be used in neurobiological model maintenance and simulation.
##
## $Id: GUI.pm 1.27 Sat, 21 Apr 2007 21:21:25 -0500 hugo $
##

##############################################################################
##'
##' Neurospaces : testbed C implementation that integrates with genesis
##'
##' Copyright (C) 1999-2008 Hugo Cornelis
##'
##' functional ideas ..	Hugo Cornelis, hugo.cornelis@gmail.com
##'
##' coding ............	Hugo Cornelis, hugo.cornelis@gmail.com
##'
##############################################################################


package Neurospaces::Project;


use strict;


use Neurospaces::Project::Modules::Morphology;


sub all_morphologies
{
    my $self = shift;

    my $project_name = $self->{name};

    my $project_root = $self->{root};

    #t replace with File::Find;

    my $result
	= [
	   sort
	   map
	   {
	       chomp; $_;
	   }
	   `find "$project_root/$project_name/morphologies" -name "*.ndf" -o -name "*.p" -o -iname "*.swc"`,
	  ];

    return $result;
}


sub load
{
    my $package = shift;

    my $options = shift;

    if (!defined $options->{name})
    {
	die "$0: need a project name";
    }

    use YAML 'LoadFile';

    my $neurospaces_config = LoadFile('/etc/neurospaces/project_browser/project_browser.yml');

    my $project_config = LoadFile("$neurospaces_config->{project_browser}->{root_directory}/$options->{name}/configuration.yml");

    my $result
	= Neurospaces::Project->new
	    (
	     {
	      config => $project_config,
	      name => $options->{name},
	      root => "$neurospaces_config->{project_browser}->{root_directory}",
	     },
	    );
}


sub new
{
    my $package = shift;

    my $options = shift || {};

    my $self
	= {
	   %$options,
	  };

    bless $self, $package;

    return $self;
}


1;


