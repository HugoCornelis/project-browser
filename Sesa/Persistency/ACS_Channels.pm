#!/usr/bin/perl -w
#
# $Id: ACS_Channels.pm,v 1.4 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::ACS_Channels;


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
		    acs_channels_database_add_template
		    acs_channels_database_create
		    acs_channels_database_exists
		    acs_channels_database_generate_definition_name
		    acs_channels_database_read
		    acs_channels_database_restore
		    acs_channels_database_specification
		    acs_channels_database_write
		   );


my $acs_channels_database_file = '/var/sems/acs/channel_database';


# read ACS channel specifications

my $sesa_specification = do "/sems/sesa/persistency/database/ACS_Channels";

my $add_acs_channels_defaults
    = {
       map
       {
	   $_ => $sesa_specification->{column_specification}->{$_}->{default};
       }
       keys %{$sesa_specification->{column_specification}},
      };

# tags that delimit the individual sections in the config file.

my $acs_channels_database_tags
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
       'acs-channels-definitions' => {
				      'config_keys' => [ 'acs_channels_definitions', ],
				      'keys' => [
						 "## -!- Sems section : acs-channels-definitions -!-\n",
						 "## -!- Sems section : end acs-channels-definitions -!-\n"
						],
				      'required' => 'yes',
				      'add_template' => {
							 'values' => $add_acs_channels_defaults,
							 'rewriters' => {
									 'NEW_NAME' => \&acs_channels_database_generate_definition_name,
									},
							},
				     },
       'acs-channels-definitions-version' => {
					     'config_keys' => [ 'acs_channels_definitions_version', ],
					     'keys' => [
							"## -!- Sems section : acs-channels-definitions-version -!-\n",
							"## -!- Sems section : end acs-channels-definitions-version -!-\n"
						       ],
					     'required' => 'yes',
					    },
#        'acs-channel-key-descriptions' => {
# 					  'config_keys' => [ 'key_descriptions', ],
# 					  'keys' => [
# 						     "## -!- Sems section : acs-channel-key-descriptions -!-\n",
# 						     "## -!- Sems section : end acs-channel-key-descriptions -!-\n"
# 						    ],
# 					  'required' => 'no',
# 				     },
      };

# ACS channel database template

my $acs_channels_database_template ='#  ACS Channel database file for Newtec SEMS
# $Id: ACS_Channels.pm,v 1.4 2005/06/03 15:43:24 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %channels
## -!- Sems section : end header -!-
## ===========================================================

my %channels;


## ===========================================================
## -!- Sems section : modification-info -!-

$channels{modification_info}
    = {
       user => "USER_NAME",
       date => "DATE",
       count => 0,
      };

## -!- Sems section : end modification-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : creation-info -!-

$channels{creation_info}
    = {
       user => "USER_NAME",
       date => "DATE",
      };

## -!- Sems section : end creation-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : acs-channels-next-ID -!-

$channels{acs_channels_next_ID}
    = 1;

## -!- Sems section : end acs-channels-next-ID -!-
## ===========================================================

## ===========================================================
## -!- Sems section : acs-channels-definitions-version -!-

$channels{acs_channels_definitions_version}
    = 1;

## -!- Sems section : end acs-channels-definitions-version -!-
## ===========================================================

## ===========================================================
## -!- Sems section : acs-channels-definitions -!-

$channels{acs_channels_definitions}
    = {
      };

## -!- Sems section : end acs-channels-definitions -!-
## ===========================================================

return \%channels;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';


# ACS channel database info table

my $acs_channels_database_info
    = {
       'name' => 'acs_channels_database',
       'filename' => $acs_channels_database_file,
       'is_valid'
       => sub { return(exists $_[1]->{acs_channels_definitions_version} && $_[1]->{acs_channels_definitions_version} == 1); },
       'specification' => $sesa_specification,
       'specification_name' => 'ACS_Channels',
       'tags' => $acs_channels_database_tags,
       'template_string' => $acs_channels_database_template,
      };


sub acs_channels_database_add_template
{
    return any_config_add_template('acs_channels_database', @_);
}


sub acs_channels_database_create
{
    return any_config_create('acs_channels_database', @_);
}


sub acs_channels_database_exists
{
    my $properties = any_config_properties('acs_channels_database', @_);

    return($properties->{exists});
}


#
# generate a unique channel definition name for the ACS channel database
#

sub acs_channels_database_generate_definition_name
{
    my $channels = shift;

    my $channel_name = shift;

    return any_config_entry_generate_definition_name($channels->{acs_channels_definitions}, $channel_name, 'numeric');
}


sub acs_channels_database_read
{
    return any_config_read('acs_channels_database', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub acs_channels_database_restore
{
    return any_config_restore('acs_channels_database', @_);
}


sub acs_channels_database_specification
{
    return any_config_specification('acs_channels_database', @_);
}


sub acs_channels_database_write
{
    return any_config_write('acs_channels_database', 'config', @_);
}


persistency_info_add('acs_channels_database', $acs_channels_database_info);


