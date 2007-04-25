#!/usr/bin/perl -w
#
# $Id: ACS_Stations.pm,v 1.3 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::ACS_Stations;


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
		    acs_stations_add_template
		    acs_stations_create
		    acs_stations_exists
		    acs_stations_generate_definition_name
		    acs_stations_generate_next_ID
		    acs_stations_read
		    acs_stations_restore
		    acs_stations_specification
		    acs_stations_write
		   );


my $acs_stations_file = '/var/sems/acs/stations';


# read ACS station specifications

my $sesa_specification = do "/sems/sesa/persistency/database/ACS_Stations";

my $add_acs_stations_defaults
    = {
       map
       {
	   $_ => $sesa_specification->{column_specification}->{$_}->{default};
       }
       keys %{$sesa_specification->{column_specification}},
      };

# tags that delimit the individual sections in the config file.

my $acs_stations_tags
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
       'acs-stations-definitions' => {
				      'config_keys' => [
							'acs_stations_definitions',
						       ],
				      'keys' => [
						 "## -!- Sems section : acs-stations-definitions -!-\n",
						 "## -!- Sems section : end acs-stations-definitions -!-\n",
						],
				      'required' => 'yes',
				      'add_template' => {
							 'values' => $add_acs_stations_defaults,
							 'rewriters' => {
									 'NEW_NAME' => \&acs_stations_generate_definition_name,
									 'NEW_ID' => \&acs_stations_generate_next_ID,
									},
							},
				     },
       'acs-stations-version' => {
			       'config_keys' => [ 'acs_stations_version', ],
			       'keys' => [
					  "## -!- Sems section : acs-stations-version -!-\n",
					  "## -!- Sems section : end acs-stations-version -!-\n",
					 ],
			       'required' => 'yes',
			      },
       'acs-stations-next-ID' => {
			       'config_keys' => [ 'acs_stations_next_ID', ],
			       'keys' => [
					  "## -!- Sems section : acs-stations-next-ID -!-\n",
					  "## -!- Sems section : end acs-stations-next-ID -!-\n",
					 ],
			       'required' => 'yes',
			      },
      };

# ACS stations template

my $acs_stations_template ='#  ACS ground station definitions file for Newtec SEMS
# $Id: ACS_Stations.pm,v 1.3 2005/06/03 15:43:24 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %stations
## -!- Sems section : end header -!-
## ===========================================================

my %stations;


## ===========================================================
## -!- Sems section : acs-stations-version -!-

$stations{acs_stations_version}
    = 1;

## -!- Sems section : end acs-stations-version -!-
## ===========================================================


## ===========================================================
## -!- Sems section : modification-info -!-

$stations{modification_info}
    = {
       user => "USER_NAME",
       date => "DATE",
       count => 0,
      };

## -!- Sems section : end modification-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : creation-info -!-

$stations{creation_info}
    = {
       user => "USER_NAME",
       date => "DATE",
      };

## -!- Sems section : end creation-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : acs-stations-next-ID -!-

$stations{acs_stations_next_ID}
    = 1;

## -!- Sems section : end acs-stations-next-ID -!-
## ===========================================================

## ===========================================================
## -!- Sems section : acs-stations-definitions -!-

$stations{acs_stations_definitions}
    = {
      };

## -!- Sems section : end acs-stations-definitions -!-
## ===========================================================

return \%stations;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';


# ACS stations info table

my $acs_stations_info
    = {
       'name' => 'acs_stations',
       'filename' => $acs_stations_file,
       'is_valid'
       => sub { return(exists $_[1]->{acs_stations_version} && $_[1]->{acs_stations_version} == 1); },
       'next_id_section' => 'acs-stations-next-ID',
       'specification' => $sesa_specification,
       'specification_name' => 'ACS_Stations',
       'tags' => $acs_stations_tags,
       'template_string' => $acs_stations_template,
      };


sub acs_stations_add_template
{
    return any_config_add_template('acs_stations', @_);
}


sub acs_stations_create
{
    return any_config_create('acs_stations', @_);
}


sub acs_stations_exists
{
    my $properties = any_config_properties('acs_stations', @_);

    return($properties->{exists});
}


#
# generate a unique station name
#

sub acs_stations_generate_definition_name
{
    my $stations = shift;

    my $station_name = shift;

    return any_config_entry_generate_definition_name($stations->{acs_stations_definitions}, $station_name, 'numeric');
}


#
# generate a unique station ID
#

sub acs_stations_generate_next_ID
{
    return any_config_generate_ID('acs_stations', @_);
}


sub acs_stations_read
{
    return any_config_read('acs_stations', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub acs_stations_restore
{
    return any_config_restore('acs_stations', @_);
}


sub acs_stations_specification
{
    return any_config_specification('acs_stations', @_);
}


sub acs_stations_write
{
    my $stations = $_[0];

    my $sections = $_[1];

    my $result = any_config_write('acs_stations', 'config', @_);

    return $result;
}


persistency_info_add('acs_stations', $acs_stations_info);


