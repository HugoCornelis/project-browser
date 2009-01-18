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


our $project_directories
    = [
       {
	description => 'directory with subdirectories with reconstructed neuronal morphologies',
	directory => 'morphologies',
	related => [
		    {
		     description => 'morphology_groups',
		     directory => 'morphology_groups',
		    },
		    {
		     description => 'network_groups',
		     directory => 'network_groups',
		    },
		    {
		     description => 'kinetic_groups',
		     directory => 'kinetic_groups',
		    },
		   ],
       },
       {
	description => 'database that groups reconstructed neuronal morphologies for further analysis',
	directory => 'morphology_groups',
       },
       {
	description => 'database with simulation definitions',
	directory => 'modules',
       },
       {
	description => 'free style pictures',
	directory => 'pictures',
       },
       {
	description => 'scripts for analysis',
	directory => 'scripts',
       },
       {
	description => 'output of analysis scripts',
	directory => 'scripts/output',
       },
       {
	description => 'colormaps of morphologies',
	directory => 'colormaps',
       },
       {
	description => 'narrative overview of the project',
	directory => 'narrative_components',
       },
       {
	description => 'summary notes of project progress',
	directory => 'summary',
       },
       {
	description => 'papers related to this project',
	directory => 'papers',
       },
       {
	description => 'models private to this project',
	directory => 'models',
       },
       {
	description => 'project component replicator',
	directory => 'replicator',
       },
      ];


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


sub create
{
    my $self = shift;

    # loop through all project directories

    foreach my $project_directory (@$project_directories)
    {
	my $directory = $project_directory->{directory};

	# create a directory

	if (!-d $directory)
	{
	    mkdir $directory;
	}

	# create the default descriptor

	my $descriptor_filename = "$directory/descriptor.yml";

	if (!-r $descriptor_filename)
	{
	    my $descriptor
		= {
		   description => $project_directory->{description},
		  };

	    use YAML "DumpFile";

	    DumpFile($descriptor_filename, $descriptor);
	}
    }
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

    my $project_config = LoadFile("$neurospaces_config->{project_browser}->{root_directory}/$options->{name}/descriptor.yml");

    my $result
	= Neurospaces::Project->new
	    (
	     {
# 	      config => $project_config,
	      name => $options->{name},
# 	      root => "$neurospaces_config->{project_browser}->{root_directory}",
	     },
	    );
}


sub new
{
    my $package = shift;

    my $options = shift || {};

    if (!defined $options->{name})
    {
	die "$0: need a project name";
    }

    use YAML 'LoadFile';

    my $neurospaces_config;

    my $neurospaces_config_filename = '/etc/neurospaces/project_browser/project_browser.yml';

    if (-r $neurospaces_config_filename)
    {
	$neurospaces_config = LoadFile($neurospaces_config_filename);
    }
    else
    {
	$neurospaces_config
	    = {
	       project_browser => {
				   root_directory => '/var/neurospaces/simulation_projects/',
				  },
	      };
    }

    my $project_config = LoadFile("$neurospaces_config->{project_browser}->{root_directory}/$options->{name}/descriptor.yml");

    my $self
	= {
	   config => $project_config,
	   name => $options->{name},
	   root => "$neurospaces_config->{project_browser}->{root_directory}",
	   %$options,
	  };

    bless $self, $package;

    return $self;
}


1;


