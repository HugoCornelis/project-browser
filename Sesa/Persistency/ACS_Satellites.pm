#!/usr/bin/perl -w
#
# $Id: ACS_Satellites.pm,v 1.5 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::ACS_Satellites;


use strict;


use Sesa::Persistency qw(
			 any_config_add_template
			 any_config_create
			 any_config_entry_generate_definition_name
			 any_config_generate_ID
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
		    acs_satellites_add_template
		    acs_satellites_create
		    acs_satellites_exists
		    acs_satellites_generate_definition_name
		    acs_satellites_generate_next_ID
		    acs_satellites_read
		    acs_satellites_restore
		    acs_satellites_specification
		    acs_satellites_write
		   );


my $acs_satellites_file = '/var/sems/acs/satellites';


# read ACS station specifications

my $sesa_specification = do "/sems/sesa/persistency/database/ACS_Satellites";

my $add_acs_satellites_defaults
    = {
       map
       {
	   $_ => $sesa_specification->{column_specification}->{$_}->{default};
       }
       keys %{$sesa_specification->{column_specification}},
      };

# tags that delimit the individual sections in the config file.

my $acs_satellites_tags
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
       'acs-satellites' => {
		       'config_keys' => [
					 'acs_satellites',
					],
		       'keys' => [
				  "## -!- Sems section : acs-satellites -!-\n",
				  "## -!- Sems section : end acs-satellites -!-\n",
				 ],
		       'required' => 'yes',
		       'add_template' => {
					  'values' => $add_acs_satellites_defaults,
					  'rewriters' => {
							  'NEW_NAME' => \&acs_satellites_generate_definition_name,
							  'NEW_ID' => \&acs_satellites_generate_next_ID,
							 },
					 },
		      },
       'acs-satellites-version' => {
			       'config_keys' => [ 'acs_satellites_version', ],
			       'keys' => [
					  "## -!- Sems section : acs-satellites-version -!-\n",
					  "## -!- Sems section : end acs-satellites-version -!-\n",
					 ],
			       'required' => 'yes',
			      },
       'acs-satellites-next-ID' => {
			       'config_keys' => [ 'acs_satellites_next_ID', ],
			       'keys' => [
					  "## -!- Sems section : acs-satellites-next-ID -!-\n",
					  "## -!- Sems section : end acs-satellites-next-ID -!-\n",
					 ],
			       'required' => 'yes',
			      },
      };

# ACS satellites template

my $acs_satellites_template ='#  ACS satellite definitions file for Newtec SEMS
# $Id: ACS_Satellites.pm,v 1.5 2005/06/03 15:43:24 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %satellites
## -!- Sems section : end header -!-
## ===========================================================

my %satellites;


## ===========================================================
## -!- Sems section : acs-satellites-version -!-

$satellites{acs_satellites_version}
    = 1;

## -!- Sems section : end acs-satellites-version -!-
## ===========================================================


## ===========================================================
## -!- Sems section : modification-info -!-

$satellites{modification_info}
    = {
       user => "USER_NAME",
       date => "DATE",
       count => 0,
      };

## -!- Sems section : end modification-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : creation-info -!-

$satellites{creation_info}
    = {
       user => "USER_NAME",
       date => "DATE",
      };

## -!- Sems section : end creation-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : acs-satellites-next-ID -!-

$satellites{acs_satellites_next_ID}
    = 1;

## -!- Sems section : end acs-satellites-next-ID -!-
## ===========================================================

## ===========================================================
## -!- Sems section : acs-satellites -!-

$satellites{acs_satellites}
    = {
      };

## -!- Sems section : end acs-satellites -!-
## ===========================================================

return \%satellites;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';


# ACS satellites info table

my $acs_satellites_info
    = {
       'name' => 'acs_satellites',
       'filename' => $acs_satellites_file,
       'is_valid'
       => sub { return(exists $_[1]->{acs_satellites_version} && $_[1]->{acs_satellites_version} == 1); },
       'next_id_section' => 'acs-satellites-next-ID',
       'specification' => $sesa_specification,
       'specification_name' => 'ACS_Satellites',
       'tags' => $acs_satellites_tags,
       'template_string' => $acs_satellites_template,
      };


sub acs_satellites_add_template
{
    return any_config_add_template('acs_satellites', @_);
}


sub acs_satellites_create
{
    return any_config_create('acs_satellites', @_);
}


sub acs_satellites_exists
{
    my $properties = any_config_properties('acs_satellites', @_);

    return($properties->{exists});
}


#
# generate a unique satellite name
#

sub acs_satellites_generate_definition_name
{
    my $satellites = shift;

    my $satellite_name = shift;

    return any_config_entry_generate_definition_name($satellites->{acs_satellites}, $satellite_name, 'numeric');
}


#
# generate a unique satellite ID
#

sub acs_satellites_generate_next_ID
{
    return any_config_generate_ID('acs_satellites', @_);
}


sub acs_satellites_read
{
    return any_config_read('acs_satellites', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub acs_satellites_restore
{
    return any_config_restore('acs_satellites', @_);
}


sub acs_satellites_specification
{
    return any_config_specification('acs_satellites', @_);
}


sub acs_satellites_write
{
    return any_config_write('acs_satellites', 'config', @_);
}


persistency_info_add('acs_satellites', $acs_satellites_info);


