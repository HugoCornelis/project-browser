#!/usr/bin/perl -w

##
## Neurospaces: a library which implements a global typed symbol table to
## be used in neurobiological model maintenance and simulation.
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


require Exporter;

our @ISA = qw(Exporter);

our @EXPORT_OK
    = qw(
	 projects_read
	);


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


sub projects_read
{
    my $self = shift;

    use YAML 'LoadFile';

    my $neurospaces_config = LoadFile('/etc/neurospaces/project_browser/project_browser.yml');

    my $project_root = $neurospaces_config->{project_browser}->{root_directory};

    #t replace with File::Find;

    my $all_projects
	= {
	   map
	   {
	       print STDERR "$_ $project_root\n";

	       my $descriptor = LoadFile("$_/descriptor.yml");

	       s(.*/)();

	       $_ => $descriptor;
	   }
	   grep
	   {
	       print STDERR "$_ $project_root\n";

	       $_ ne $project_root
	   }
	   map
	   {
	       chomp; $_;
	   }
	   `find "$project_root" -maxdepth 1 -type d`,
	  };

    my $result
	= {
	   projects => $all_projects,
	  };

    return $result;
}


sub create
{
    my $self = shift;

    # create project directory

    my $directory = "$self->{root}/$self->{name}";

    if (!-d $directory)
    {
	mkdir $directory;
    }

    # create project descriptor

    my $descriptor_filename = "$directory/descriptor.yml";

    if (!-r $descriptor_filename)
    {
	my $descriptor
	    = {
	       description => $self->{description},
	      };

	use YAML "DumpFile";

	DumpFile($descriptor_filename, $descriptor);
    }

    # loop through all project directories

    foreach my $project_directory (@$project_directories)
    {
	my $directory = "$self->{root}/$self->{name}/$project_directory->{directory}";

	# create directory

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

#     my $project_config = LoadFile("$neurospaces_config->{project_browser}->{root_directory}/$options->{name}/descriptor.yml");

    my $self
	= {
# 	   config => $project_config,
	   name => $options->{name},
	   root => "$neurospaces_config->{project_browser}->{root_directory}",
	   %$options,
	  };

    bless $self, $package;

    return $self;
}


1;


