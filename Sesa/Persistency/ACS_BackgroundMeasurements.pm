#!/usr/bin/perl -w
#
# $Id: ACS_BackgroundMeasurements.pm,v 1.3 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::ACS_BackgroundMeasurements;


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
		    acs_background_measurements_add_template
		    acs_background_measurements_create
		    acs_background_measurements_exists
		    acs_background_measurements_generate_definition_name
		    acs_background_measurements_generate_next_ID
		    acs_background_measurements_read
		    acs_background_measurements_restore
		    acs_background_measurements_specification
		    acs_background_measurements_write
		   );


my $acs_background_measurements_file = '/var/sems/acs/background_measurements';


# read ACS band specifications

my $sesa_specification = do "/sems/sesa/persistency/database/ACS_BackgroundMeasurements";

my $add_acs_background_measurements_spectrum_capture_defaults
    = {
       map
       {
	   $_ => $sesa_specification->{column_specifications}->{spectrum_capture}->{column_specification}->{$_}->{default};
       }
       keys %{$sesa_specification->{column_specifications}->{spectrum_capture}->{column_specification}},
      };

# ACS background measurement default values.

my $add_acs_background_measurements_defaults
    = {
#        "ID" => 'NEW_ID',
       "Activity Name" => 'NEW_NAME',
       "type" => 'Spectrum', # 'Carrier', 'Beacon' (type of signal), or 'Spectrum', 'Beacon Level' (type of view)
       "satellite-name" => 'Arabsat',
       "channel-name" => 'C-band',
       "start-frequency" => '234234000',
       "end-frequency" => '334234000',
       'matrix-input-port' => 1,
       'local-oscillator' => '9.8GHz',
       'ntcSeEqSaRefLevel' => '23dB',
       'ntcSeEqMeSaYaxisScal' => 1,
       'SA-resolution-bandwidth' => 100,
       'preferred-SA' => 1,
       'enabled' => 0,
       'update-time' => '10s'
      };

# ACS background measurement default values (beacon level).

my $add_acs_background_measurements_beacon_level_defaults
    = {
#        "ID" => 'NEW_ID',
       "Activity Name" => 'NEW_NAME',
       "type" => 'ntcSeEqACSBeaconBeacon', # 'Carrier', 'Beacon' (type of signal), or 'Spectrum', 'Beacon Level' (type of view)
       "satellite-name" => 'Arabsat',
       "channel-name" => 'C-band',
       ntcSeEqACSBackGroundMonDevice => 'Beacon',
       ntcSeEqACSBackGroundBeaconLO => '9500000000',
       ntcSeEqACSBackGroundBeaconRFfreq => '873245',
       ntcSeEqACSBackGroundMatrixAgent => 'MATRIX',
       ntcSeEqACSBackGroundMatrixInput => 1,
       ntcSeEqACSBackGroundMatrixOutput => 2,
       'enabled' => 0,
       'update-time' => '10s'
      };

# ACS background measurement default values (beacon level).

my $add_acs_background_measurements_beacon_level_SA_defaults
    = {
#        "ID" => 'NEW_ID',
       "Activity Name" => 'NEW_NAME',
       "type" => 'ntcSeEqACSBeaconSa', # 'Carrier', 'Beacon' (type of signal), or 'Spectrum', 'Beacon Level' (type of view)
       "satellite-name" => 'Arabsat',
       "channel-name" => 'C-band',
       ntcSeEqACSBackGroundMonDevice => 'SA',
       ntcSeEqACSBackGroundBeaconRFfreq => '873245',
       ntcSeEqACSBackGroundBeaconLO => '9500000000',
       ntcSeEqACSBackGroundMatrixAgent => 'MATRIX',
       ntcSeEqACSBackGroundMatrixInput => 1,
       ntcSeEqACSBackGroundMatrixOutput => 2,
       'preferred-SA' => 1,
       'enabled' => 0,
       'update-time' => '10s'
      };

# # ACS background measurement default values (beacon level).

# my $add_acs_background_measurements_spectrum_capture_defaults
#     = {
# #        "ID" => 'NEW_ID',
#        "Activity Name" => 'NEW_NAME',
#        "type" => 'ntcSeEqACSSpectrumCapture', # 'Carrier', 'Beacon' (type of signal), or 'Spectrum', 'Beacon Level' (type of view)
#        "satellite-name" => 'Arabsat',
#        "channel-name" => 'C-band',
#        ntcSeEqSaStartRFfreq => '9873245',
#        ntcSeEqSaStopRFfreq => '324234',
#        ntcSeEqSaRefLevel => '23',
#        ntcSeEqSaLO => '9500000000',
#        ntcSeEqSaResBW => '3245243',
#        ntcSeEqSaVidBW => '234234',
#        ntcSeEqACSBackGroundMonDevice => '1',
#        ntcSeEqACSBackGroundMatrixAgent => 'MATRIX',
#        ntcSeEqMatrixInput => 1,
#        ntcSeEqMatrixOutput => 2,
#        ntcSeEqMeSaYaxisScal => 1000,
#        'preferred-SA' => 1,
#        'enabled' => 0,
#        'update-time' => '10s'
#       };

# tags that delimit the individual sections in the config file.

my $acs_background_measurements_tags
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
       'acs-background-measurements' => {
# 					 'config_keys' => [
# 							   'acs_background_measurements_beacons',
# 							   'acs_background_measurements_spectrums',
# 							  ],
					 'config_keys' => [
							   'acs_background_measurements',
							  ],
					 'keys' => [
						    "## -!- Sems section : acs-background-measurements -!-\n",
						    "## -!- Sems section : end acs-background-measurements -!-\n",
						   ],
					 'required' => 'yes',
# 					 'add_template' => {
# 							    'values' => $add_acs_background_measurements_defaults,
# 							    'rewriters' => {
# 									    'NEW_NAME' => \&acs_background_measurements_generate_definition_name,
# 									    'NEW_ID' => \&acs_background_measurements_generate_next_ID,
# 									   },
# 							   },
					},
       'acs-background-measurements-beacon-level' => {
						      'add_template' => {
									 'values' => $add_acs_background_measurements_beacon_level_defaults,
									 'rewriters' => {
											 'NEW_NAME' => \&acs_background_measurements_generate_definition_name,
											 'NEW_ID' => \&acs_background_measurements_generate_next_ID,
											},
									},
						     },
       'acs-background-measurements-beacon-level-SA' => {
							 'add_template' => {
									    'values' => $add_acs_background_measurements_beacon_level_SA_defaults,
									    'rewriters' => {
											    'NEW_NAME' => \&acs_background_measurements_generate_definition_name,
											    'NEW_ID' => \&acs_background_measurements_generate_next_ID,
											   },
									},
						     },
       'acs-background-measurements-spectrum-capture' => {
							  'add_template' => {
									     'values' => $add_acs_background_measurements_spectrum_capture_defaults,
									     'rewriters' => {
											     'NEW_NAME' => \&acs_background_measurements_generate_definition_name,
											     'NEW_ID' => \&acs_background_measurements_generate_next_ID,
											    },
									    },
							 },
       'acs-background-measurements-version' => {
						 'config_keys' => [ 'acs_background_measurements_version', ],
						 'keys' => [
							    "## -!- Sems section : acs-background-measurements-version -!-\n",
							    "## -!- Sems section : end acs-background-measurements-version -!-\n",
							   ],
						 'required' => 'yes',
						},
       'acs-background-measurements-next-ID' => {
						'config_keys' => [ 'acs_background_measurements_next_ID', ],
						'keys' => [
							   "## -!- Sems section : acs-background-measurements-next-ID -!-\n",
							   "## -!- Sems section : end acs-background-measurements-next-ID -!-\n",
							  ],
						'required' => 'yes',
					       },
#        'acs-background-measurements-key-descriptions' => {
# 					  'config_keys' => [ 'key_descriptions', ],
# 					  'keys' => [
# 						     "## -!- Sems section : acs-channel-key-descriptions -!-\n",
# 						     "## -!- Sems section : end acs-channel-key-descriptions -!-\n",
# 						    ],
# 					  'required' => 'no',
# 				     },
      };

# ACS background measurements template

my $acs_background_measurements_template ='#  ACS Background Measurements file for Newtec SEMS
# $Id: ACS_BackgroundMeasurements.pm,v 1.3 2005/06/03 15:43:24 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %measurements
## -!- Sems section : end header -!-
## ===========================================================

my %measurements;


## ===========================================================
## -!- Sems section : acs-background-measurements-version -!-

$measurements{acs_background_measurements_version}
    = 1;

## -!- Sems section : end acs-background-measurements-version -!-
## ===========================================================


## ===========================================================
## -!- Sems section : modification-info -!-

$measurements{modification_info}
    = {
       user => "USER_NAME",
       date => "DATE",
       count => 0,
      };

## -!- Sems section : end modification-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : creation-info -!-

$measurements{creation_info}
    = {
       user => "USER_NAME",
       date => "DATE",
      };

## -!- Sems section : end creation-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : acs-background-measurements-next-ID -!-

$measurements{acs_background_measurements_next_ID}
    = 1;

## -!- Sems section : end acs-background-measurements-next-ID -!-
## ===========================================================

## ===========================================================
## -!- Sems section : acs-background-measurements -!-

$measurements{acs_background_measurements}
    = {
      };

## -!- Sems section : end acs-background-measurements -!-
## ===========================================================

return \%measurements;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';


# ACS background measurements info table

my $acs_background_measurements_info
    = {
       'name' => 'acs_background_measurements',
       'filename' => $acs_background_measurements_file,
       'is_valid'
       => sub { return(exists $_[1]->{acs_background_measurements_version} && $_[1]->{acs_background_measurements_version} == 1); },
       'next_id_section' => 'acs-background-measurements-next-ID',
       'specification' => $sesa_specification,
       'specification_name' => 'ACS_BackgroundMeasurements',
       'tags' => $acs_background_measurements_tags,
       'template_string' => $acs_background_measurements_template,
      };


sub acs_background_measurements_add_template
{
    return any_config_add_template('acs_background_measurements', @_);
}


sub acs_background_measurements_create
{
    return any_config_create('acs_background_measurements', @_);
}


sub acs_background_measurements_exists
{
    my $properties = any_config_properties('acs_background_measurements', @_);

    return($properties->{exists});
}


#
# generate a unique measurement definition name
#

sub acs_background_measurements_generate_definition_name
{
    my $measurements = shift;

    my $measurement_name = shift;

    return any_config_entry_generate_definition_name($measurements->{acs_background_measurements}, $measurement_name, 'numeric');
}


#
# generate a unique measurement ID
#

sub acs_background_measurements_generate_next_ID
{
    return any_config_generate_ID('acs_background_measurements', @_);
}


sub acs_background_measurements_read
{
    return any_config_read('acs_background_measurements', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub acs_background_measurements_restore
{
    return any_config_restore('acs_background_measurements', @_);
}


sub acs_background_measurements_specification
{
    return any_config_specification('acs_background_measurements', @_);
}


sub acs_background_measurements_write
{
    return any_config_write('acs_background_measurements', 'config', @_);
}


persistency_info_add('acs_background_measurements', $acs_background_measurements_info);


