#!/usr/bin/perl -w
#
# $Id: Test_Zone.pm,v 1.1 2005/07/18 14:21:35 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::Test_Zone;


use strict;


# 			 any_config_add_template
# 			 any_config_create
# 			 any_config_entry_generate_definition_name
# 			 any_config_properties
# 			 any_config_read
# 			 any_config_restore
# 			 any_config_specification
# 			 any_config_write
use Sesa::Persistency qw(
			 persistency_info_add
			);


require Exporter;


our @ISA = qw(Exporter);

# 		    acs_channels_database_add_template
# 		    acs_channels_database_create
# 		    acs_channels_database_exists
# 		    acs_channels_database_generate_definition_name
# 		    acs_channels_database_read
# 		    acs_channels_database_restore
# 		    acs_channels_database_specification
# 		    acs_channels_database_write
our @EXPORT_OK = qw(
		    test_zone_add_template
		    test_zone_generate_definition_name
		    test_zone_read
		    test_zone_specification
		    test_zone_write
		   );


# hardcoded output of `zoneadm list -c -v`

my $zones
    = [
       {
	id => 0,
	name => 'global',
        path => '/',
	status => 'running',
       },
       {
	id => 2,
	name => 'webserver',
        path => '/zones/webserver',
        status => 'running',
       },
       {
	id => 6,
	name => 'mailserver',
        path => '/zones/mailserver',
	status => 'running',
       },
       {
	id => 9,
	name => 'fileserver',
        path => '/zones/fileserver',
	status => 'running',
       },
       {
	id => 14,
	name => 'test3',
        path => '/zones/test3',
	status => 'running',
       },
      ];


# read zone specifications

my $sesa_specification = do "/sems/sesa/persistency/database/Test_Zones";

my $add_test_zone_defaults
    = {
       map
       {
	   $_ => $sesa_specification->{column_specification}->{$_}->{default};
       }
       keys %{$sesa_specification->{column_specification}},
      };

# tags that delimit the individual sections in the config file.

# my $test_zone_tags
#     = {
#        'modification-info' => {
# 			       'config_keys' => [
# 						 'modification_info',
# 						],
# 			       'keys' => [
# 					  "## -!- Sems section : modification-info -!-\n",
# 					  "## -!- Sems section : end modification-info -!-\n",
# 					 ],
# 			       'required' => 'yes',
# 			       'shared' => 'global',
# 			      },
#        'creation-info' => {
# 			   'config_keys' => [
# 					     'creation_info',
# 					    ],
# 			   'keys' => [
# 				      "## -!- Sems section : creation-info -!-\n",
# 				      "## -!- Sems section : end creation-info -!-\n",
# 				     ],
# 			   'required' => 'yes',
# 			   'shared' => 'global',
# 			  },
#        'test-zone-definitions' => {
# 				   'config_keys' => [ 'test_zone_definitions', ],
# 				   'keys' => [
# 					      "## -!- Sems section : test-zone-definitions -!-\n",
# 					      "## -!- Sems section : end test-zone-definitions -!-\n"
# 					     ],
# 				   'required' => 'yes',
# 				   'add_template' => {
# 						      'values' => $add_test_zone_defaults,
# 						      'rewriters' => {
# 								      'NEW_NAME' => \&test_zone_generate_definition_name,
# 								     },
# 						     },
# 				  },
#        'test-zone-definitions-version' => {
# 					   'config_keys' => [ 'test_zone_definitions_version', ],
# 					   'keys' => [
# 						      "## -!- Sems section : acs-channels-definitions-version -!-\n",
# 						      "## -!- Sems section : end acs-channels-definitions-version -!-\n"
# 						     ],
# 					   'required' => 'yes',
# 					  },
#       };

# # ACS channel database template

# my $acs_channels_database_template ='#  ACS Channel database file for Newtec SEMS
# # $Id: Test_Zone.pm,v 1.1 2005/07/18 14:21:35 hco Exp $
# #
# ## ===========================================================
# ## -!- Sems section : header -!-
# ## sems_variable_name %channels
# ## -!- Sems section : end header -!-
# ## ===========================================================

# my %channels;


# ## ===========================================================
# ## -!- Sems section : modification-info -!-

# $channels{modification_info}
#     = {
#        user => "USER_NAME",
#        date => "DATE",
#        count => 0,
#       };

# ## -!- Sems section : end modification-info -!-
# ## ===========================================================


# ## ===========================================================
# ## -!- Sems section : creation-info -!-

# $channels{creation_info}
#     = {
#        user => "USER_NAME",
#        date => "DATE",
#       };

# ## -!- Sems section : end creation-info -!-
# ## ===========================================================


# ## ===========================================================
# ## -!- Sems section : acs-channels-next-ID -!-

# $channels{acs_channels_next_ID}
#     = 1;

# ## -!- Sems section : end acs-channels-next-ID -!-
# ## ===========================================================

# ## ===========================================================
# ## -!- Sems section : acs-channels-definitions-version -!-

# $channels{acs_channels_definitions_version}
#     = 1;

# ## -!- Sems section : end acs-channels-definitions-version -!-
# ## ===========================================================

# ## ===========================================================
# ## -!- Sems section : acs-channels-definitions -!-

# $channels{acs_channels_definitions}
#     = {
#       };

# ## -!- Sems section : end acs-channels-definitions -!-
# ## ===========================================================

# return \%channels;


# ## ======================================================================
# ## Local Variables:
# ## mode:               Cperl
# ## cperl-indent-level: 4
# ## End:
# ';


# test zone info table

my $test_zone_info
    = {
       'name' => 'test_zone',
#        'filename' => $acs_channels_database_file,
#        'is_valid'
#        => sub { return(exists $_[1]->{acs_channels_definitions_version} && $_[1]->{acs_channels_definitions_version} == 1); },
#        'specification' => $sesa_specification,
       'specification_name' => 'test_zone',
#        'tags' => $acs_channels_database_tags,
#        'template_string' => $acs_channels_database_template,
      };


sub test_zone_add_template
{
    return { %$add_test_zone_defaults, };
}


sub test_zone_generate_definition_name
{
}


sub test_zone_read
{
}


sub test_zone_specification
{
    return $sesa_specification;
}


sub test_zone_write
{
}


persistency_info_add('test_zone', $test_zone_info);


