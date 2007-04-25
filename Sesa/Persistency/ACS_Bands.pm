#!/usr/bin/perl -w
#
# $Id: ACS_Bands.pm,v 1.4 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::ACS_Bands;


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
		    acs_bands_add_template
		    acs_bands_create
		    acs_bands_exists
		    acs_bands_generate_definition_name
		    acs_bands_generate_next_ID
		    acs_bands_read
		    acs_bands_restore
		    acs_bands_specification
		    acs_bands_write
		   );


my $acs_bands_file = '/var/sems/acs/bands';


# read ACS band specifications

my $sesa_specification = do "/sems/sesa/persistency/database/ACS_Bands";

my $add_acs_bands_defaults
    = {
       map
       {
	   $_ => $sesa_specification->{column_specification}->{$_}->{default};
       }
       keys %{$sesa_specification->{column_specification}},
      };

# tags that delimit the individual sections in the config file.

my $acs_bands_tags
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
       'acs-bands' => {
		       'config_keys' => [
					 'acs_bands',
					],
		       'keys' => [
				  "## -!- Sems section : acs-bands -!-\n",
				  "## -!- Sems section : end acs-bands -!-\n",
				 ],
		       'required' => 'yes',
		       'add_template' => {
					  'values' => $add_acs_bands_defaults,
					  'rewriters' => {
							  'NEW_NAME' => \&acs_bands_generate_definition_name,
							  'NEW_ID' => \&acs_bands_generate_next_ID,
							 },
					 },
		      },
       'acs-bands-version' => {
			       'config_keys' => [ 'acs_bands_version', ],
			       'keys' => [
					  "## -!- Sems section : acs-bands-version -!-\n",
					  "## -!- Sems section : end acs-bands-version -!-\n",
					 ],
			       'required' => 'yes',
			      },
       'acs-bands-next-ID' => {
			       'config_keys' => [ 'acs_bands_next_ID', ],
			       'keys' => [
					  "## -!- Sems section : acs-bands-next-ID -!-\n",
					  "## -!- Sems section : end acs-bands-next-ID -!-\n",
					 ],
			       'required' => 'yes',
			      },
      };

# ACS bands measurements template

my $acs_bands_template ='#  ACS satellite band definitions file for Newtec SEMS
# $Id: ACS_Bands.pm,v 1.4 2005/06/03 15:43:24 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %bands
## -!- Sems section : end header -!-
## ===========================================================

my %bands;


## ===========================================================
## -!- Sems section : acs-bands-version -!-

$bands{acs_bands_version}
    = 1;

## -!- Sems section : end acs-bands-version -!-
## ===========================================================


## ===========================================================
## -!- Sems section : modification-info -!-

$bands{modification_info}
    = {
       user => "USER_NAME",
       date => "DATE",
       count => 0,
      };

## -!- Sems section : end modification-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : creation-info -!-

$bands{creation_info}
    = {
       user => "USER_NAME",
       date => "DATE",
      };

## -!- Sems section : end creation-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : acs-bands-next-ID -!-

$bands{acs_bands_next_ID}
    = 1;

## -!- Sems section : end acs-bands-next-ID -!-
## ===========================================================

## ===========================================================
## -!- Sems section : acs-bands -!-

$bands{acs_bands}
    = {
      };

## -!- Sems section : end acs-bands -!-
## ===========================================================

return \%bands;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';


# ACS bands info table

my $acs_bands_info
    = {
       'name' => 'acs_bands',
       'filename' => $acs_bands_file,
       'is_valid'
       => sub { return(exists $_[1]->{acs_bands_version} && $_[1]->{acs_bands_version} == 1); },
       'next_id_section' => 'acs-bands-next-ID',
       'specification' => $sesa_specification,
       'specification_name' => 'ACS_Bands',
       'tags' => $acs_bands_tags,
       'template_string' => $acs_bands_template,
      };


sub acs_bands_add_template
{
    return any_config_add_template('acs_bands', @_);
}


sub acs_bands_create
{
    return any_config_create('acs_bands', @_);
}


sub acs_bands_exists
{
    my $properties = any_config_properties('acs_bands', @_);

    return($properties->{exists});
}


#
# generate a unique band name
#

sub acs_bands_generate_definition_name
{
    my $bands = shift;

    my $band_name = shift;

    return any_config_entry_generate_definition_name($bands->{acs_bands}, $band_name, 'numeric');
}


#
# generate a unique band ID
#

sub acs_bands_generate_next_ID
{
    return any_config_generate_ID('acs_bands', @_);
}


sub acs_bands_read
{
    return any_config_read('acs_bands', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub acs_bands_restore
{
    return any_config_restore('acs_bands', @_);
}


sub acs_bands_specification
{
    return any_config_specification('acs_bands', @_);
}


sub acs_bands_write
{
    my $bands = $_[0];

    my $sections = $_[1];

    my $result = any_config_write('acs_bands', 'config', @_);

    # if the beacon definitions have been changed

    if ($result && grep { /^acs-bands$/ } @$sections)
    {
	# push the beacon definitions to the background measurements database

	require NTC::ACS::ACS_Database_Interface;

	my $acs_database = NTC::ACS::ACS_Database_Interface->new();

	$result = $acs_database->push_bands();
    }

    return $result;
}


persistency_info_add('acs_bands', $acs_bands_info);


