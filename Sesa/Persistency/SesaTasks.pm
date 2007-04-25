#!/usr/bin/perl -w
#
# $Id: SesaTasks.pm,v 1.1 2005/07/29 15:25:28 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::SesaTasks;


use strict;


use Sesa::Persistency qw(
			 any_config_add_template
			 any_config_create
			 any_config_entry_generate_definition_name
			 any_config_properties
			 any_config_read
			 any_config_restore
			 any_config_specification
			 any_config_write
			 persistency_info_add
			);


require Exporter;


our @ISA = qw(Exporter);

our @EXPORT_OK = qw(
		    sesa_tasks_add_template
		    sesa_tasks_create
		    sesa_tasks_exists
		    sesa_tasks_generate_definition_name
		    sesa_tasks_read
		    sesa_tasks_restore
		    sesa_tasks_specification
		    sesa_tasks_write
		   );


my $sesa_tasks_file = '/sems/sesa/development/tasks';


# read sesa_tasks specifications

my $sesa_specification = do "/sems/sesa/persistency/database/SesaTasks";

my $add_sesa_tasks_defaults
    = {
       map
       {
	   $_ => $sesa_specification->{column_specification}->{$_}->{default};
       }
       keys %{$sesa_specification->{column_specification}},
      };

# tags that delimit the individual sections in the config file.

my $sesa_tasks_tags
    = {
       'modification-info' => {
			       'config_keys' => [
						 'modification_info',
						],
			       'keys' => [
					  "## -!- Sems section : modification-info -!-\n",
					  "## -!- Sems section : end modification-info -!-\n",
					 ],
			       'required' => 'yes',
			       'shared' => 'global',
			      },
       'creation-info' => {
			   'config_keys' => [
					     'creation_info',
					    ],
			   'keys' => [
				      "## -!- Sems section : creation-info -!-\n",
				      "## -!- Sems section : end creation-info -!-\n",
				     ],
			   'required' => 'yes',
			   'shared' => 'global',
			  },
       'sesa-tasks-definitions' => {
				      'config_keys' => [ 'sesa_tasks_definitions', ],
				      'keys' => [
						 "## -!- Sems section : sesa-tasks-definitions -!-\n",
						 "## -!- Sems section : end sesa-tasks-definitions -!-\n"
						],
				      'required' => 'yes',
				      'add_template' => {
							 'values' => $add_sesa_tasks_defaults,
							 'rewriters' => {
									 'NEW_NAME' => \&sesa_tasks_generate_definition_name,
									},
							},
				     },
       'sesa-tasks-definitions-version' => {
					     'config_keys' => [ 'sesa_tasks_definitions_version', ],
					     'keys' => [
							"## -!- Sems section : sesa-tasks-definitions-version -!-\n",
							"## -!- Sems section : end sesa-tasks-definitions-version -!-\n"
						       ],
					     'required' => 'yes',
					    },
      };

# sesa_tasks database template

my $sesa_tasks_template ='#  Sesa tasks
# $Id: SesaTasks.pm,v 1.1 2005/07/29 15:25:28 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %tasks
## -!- Sems section : end header -!-
## ===========================================================

my %tasks;


## ===========================================================
## -!- Sems section : modification-info -!-

$tasks{modification_info}
    = {
       user => "USER_NAME",
       date => "DATE",
       count => 0,
      };

## -!- Sems section : end modification-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : creation-info -!-

$tasks{creation_info}
    = {
       user => "USER_NAME",
       date => "DATE",
      };

## -!- Sems section : end creation-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : sesa-tasks-next-ID -!-

$tasks{sesa_tasks_next_ID}
    = 1;

## -!- Sems section : end sesa-tasks-next-ID -!-
## ===========================================================

## ===========================================================
## -!- Sems section : sesa-tasks-definitions-version -!-

$tasks{sesa_tasks_definitions_version}
    = 1;

## -!- Sems section : end sesa-tasks-definitions-version -!-
## ===========================================================

## ===========================================================
## -!- Sems section : sesa-tasks-definitions -!-

$tasks{sesa_tasks_definitions}
    = {
      };

## -!- Sems section : end sesa-tasks-definitions -!-
## ===========================================================

return \%tasks;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';


# sesa_tasks database info table

my $sesa_tasks_info
    = {
       'name' => 'sesa_tasks',
       'filename' => $sesa_tasks_file,
       'is_valid'
       => sub { return(exists $_[1]->{sesa_tasks_definitions_version} && $_[1]->{sesa_tasks_definitions_version} == 1); },
       'specification' => $sesa_specification,
       'specification_name' => 'SesaTasks',
       'tags' => $sesa_tasks_tags,
       'template_string' => $sesa_tasks_template,
      };


sub sesa_tasks_add_template
{
    return any_config_add_template('sesa_tasks', @_);
}


sub sesa_tasks_create
{
    return any_config_create('sesa_tasks', @_);
}


sub sesa_tasks_exists
{
    my $properties = any_config_properties('sesa_tasks', @_);

    return($properties->{exists});
}


#
# generate a unique task definition name for the sesa_tasks database
#

sub sesa_tasks_generate_definition_name
{
    my $tasks = shift;

    my $task_name = shift;

    return any_config_entry_generate_definition_name($tasks->{sesa_tasks_definitions}, $task_name, 'numeric');
}


sub sesa_tasks_read
{
    return any_config_read('sesa_tasks', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub sesa_tasks_restore
{
    return any_config_restore('sesa_tasks', @_);
}


sub sesa_tasks_specification
{
    return any_config_specification('sesa_tasks', @_);
}


sub sesa_tasks_write
{
    return any_config_write('sesa_tasks', 'config', @_);
}


persistency_info_add('sesa_tasks', $sesa_tasks_info);


