#!/usr/bin/perl -w
#
# $Id: UPC_BackgroundMeasurements.pm,v 1.2 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::UPC_BackgroundMeasurements;


use strict;


use Sesa::Persistency qw(
			 any_config_add_template
			 any_config_create
			 any_config_entry_generate_definition_name
			 any_config_generate_ID
			 any_config_properties
			 any_config_read
			 any_config_restore
			 any_config_write
			 persistency_info_add
			);


require Exporter;


our @ISA = qw(Exporter);

our @EXPORT_OK = qw(
		    upc_background_measurements_add_template
		    upc_background_measurements_create
		    upc_background_measurements_exists
		    upc_background_measurements_generate_definition_name
		    upc_background_measurements_generate_next_ID
		    upc_background_measurements_read
		    upc_background_measurements_restore
		    upc_background_measurements_write
		   );



my $upc_background_measurements_file = '/var/sems/upc/background_measurements';


# UPC background measurement default values.

my $add_upc_background_measurements_defaults
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

# UPC background measurement default values (beacon level).

my $add_upc_background_measurements_beacon_level_defaults
    = {
#        "ID" => 'NEW_ID',
       "Activity Name" => 'NEW_NAME',
       type => "ntcSeEqUPCBeaconPower",
       ntcSeEqUPCMonDevice => "BEACON_RCVR",
       'enabled' => 0,
      };

# UPC background measurement default values (beacon level).

my $add_upc_background_measurements_beacon_level_SA_defaults
    = {
#        "ID" => 'NEW_ID',
       "Activity Name" => 'NEW_NAME',
       "type" => 'ntcSeEqUPCBeaconSa', # 'Carrier', 'Beacon' (type of signal), or 'Spectrum', 'Beacon Level' (type of view)
       "satellite-name" => 'Arabsat',
       "channel-name" => 'C-band',
       ntcSeEqUPCBackGroundMonDevice => 'SA',
       ntcSeEqUPCBackGroundBeaconRFfreq => '873245',
       ntcSeEqUPCBackGroundBeaconLO => '9500000000',
       ntcSeEqUPCBackGroundMatrixAgent => 'MATRIX',
       ntcSeEqUPCBackGroundMatrixInput => 1,
       ntcSeEqUPCBackGroundMatrixOutput => 2,
       'preferred-SA' => 1,
       'enabled' => 0,
       'update-time' => '10s'
      };

# UPC background measurement default values (beacon level).

my $add_upc_background_measurements_spectrum_capture_defaults
    = {
#        "ID" => 'NEW_ID',
       "Activity Name" => 'NEW_NAME',
       "type" => 'ntcSeEqUPCSpectrumCapture', # 'Carrier', 'Beacon' (type of signal), or 'Spectrum', 'Beacon Level' (type of view)
       "satellite-name" => 'Arabsat',
       "channel-name" => 'C-band',
       ntcSeEqSaStartRFfreq => '9873245',
       ntcSeEqSaStopRFfreq => '324234',
       ntcSeEqSaRefLevel => '23',
       ntcSeEqSaLO => '9500000000',
       ntcSeEqSaResBW => '3245243',
       ntcSeEqSaVidBW => '234234',
       ntcSeEqUPCBackGroundMonDevice => '1',
       ntcSeEqUPCBackGroundMatrixAgent => 'MATRIX',
       ntcSeEqMatrixInput => 1,
       ntcSeEqMatrixOutput => 2,
       ntcSeEqMeSaYaxisScal => 1000,
       'preferred-SA' => 1,
       'enabled' => 0,
       'update-time' => '10s'
      };

# tags that delimit the individual sections in the config file.

my $upc_background_measurements_tags
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
       'upc-background-measurements' => {
# 					 'config_keys' => [
# 							   'upc_background_measurements_beacons',
# 							   'upc_background_measurements_spectrums',
# 							  ],
					 'config_keys' => [
							   'upc_background_measurements',
							  ],
					 'keys' => [
						    "## -!- Sems section : upc-background-measurements -!-\n",
						    "## -!- Sems section : end upc-background-measurements -!-\n",
						   ],
					 'required' => 'yes',
# 					 'add_template' => {
# 							    'values' => $add_upc_background_measurements_defaults,
# 							    'rewriters' => {
# 									    'NEW_NAME' => \&upc_background_measurements_generate_definition_name,
# 									    'NEW_ID' => \&upc_background_measurements_generate_next_ID,
# 									   },
# 							   },
					},
       'upc-background-measurements-beacon-level' => {
						      'add_template' => {
									 'values' => $add_upc_background_measurements_beacon_level_defaults,
									 'rewriters' => {
											 'NEW_NAME' => \&upc_background_measurements_generate_definition_name,
											 'NEW_ID' => \&upc_background_measurements_generate_next_ID,
											},
									},
						     },
       'upc-background-measurements-beacon-level-SA' => {
							 'add_template' => {
									    'values' => $add_upc_background_measurements_beacon_level_SA_defaults,
									    'rewriters' => {
											    'NEW_NAME' => \&upc_background_measurements_generate_definition_name,
											    'NEW_ID' => \&upc_background_measurements_generate_next_ID,
											   },
									},
						     },
       'upc-background-measurements-spectrum-capture' => {
							  'add_template' => {
									     'values' => $add_upc_background_measurements_spectrum_capture_defaults,
									     'rewriters' => {
											     'NEW_NAME' => \&upc_background_measurements_generate_definition_name,
											     'NEW_ID' => \&upc_background_measurements_generate_next_ID,
											    },
									    },
							 },
       'upc-background-measurements-version' => {
						 'config_keys' => [ 'upc_background_measurements_version', ],
						 'keys' => [
							    "## -!- Sems section : upc-background-measurements-version -!-\n",
							    "## -!- Sems section : end upc-background-measurements-version -!-\n",
							   ],
						 'required' => 'yes',
						},
       'upc-background-measurements-next-ID' => {
						'config_keys' => [ 'upc_background_measurements_next_ID', ],
						'keys' => [
							   "## -!- Sems section : upc-background-measurements-next-ID -!-\n",
							   "## -!- Sems section : end upc-background-measurements-next-ID -!-\n",
							  ],
						'required' => 'yes',
					       },
      };

# UPC background measurements template
#
# note : automatically adds one entry to the table.
#

my $upc_background_measurements_template ='#  UPC Background Measurements file for Newtec SEMS
# $Id: UPC_BackgroundMeasurements.pm,v 1.2 2005/06/03 15:43:24 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %measurements
## -!- Sems section : end header -!-
## ===========================================================

my %measurements;


## ===========================================================
## -!- Sems section : upc-background-measurements-version -!-

$measurements{upc_background_measurements_version}
    = 1;

## -!- Sems section : end upc-background-measurements-version -!-
## ===========================================================


## ===========================================================
## -!- Sems section : modification-info -!-

$measurements{modification_info}
    = {
       user => "not implemented yet",
       date => "Thu Feb 10 12:07:10 2005",
       count => 0,
      };

## -!- Sems section : end modification-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : creation-info -!-

$measurements{creation_info}
    = {
       user => "not implemented yet",
       date => "Thu Feb 10 12:07:10 2005",
      };

## -!- Sems section : end creation-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : upc-background-measurements-next-ID -!-

$measurements{upc_background_measurements_next_ID}
    = 1;

## -!- Sems section : end upc-background-measurements-next-ID -!-
## ===========================================================

## ===========================================================
## -!- Sems section : upc-background-measurements -!-

$measurements{upc_background_measurements}->{"beacon-measurement"}
    = {
       type => "ntcSeEqUPCBeaconPower",
       ntcSeEqUPCMonDevice => "BEACON_RCVR",
       ID => 1,
       enabled => 1,
      };

## -!- Sems section : end upc-background-measurements -!-
## ===========================================================

return \%measurements;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';


# UPC background measurements info table

my $upc_background_measurements_info
    = {
       'name' => 'upc_background_measurements',
       'filename' => $upc_background_measurements_file,
       'is_valid'
       => sub { return(exists $_[1]->{upc_background_measurements_version} && $_[1]->{upc_background_measurements_version} == 1); },
       'next_id_section' => 'upc-background-measurements-next-ID',
       'tags' => $upc_background_measurements_tags,
       'template_string' => $upc_background_measurements_template,
      };


sub upc_background_measurements_add_template
{
    return any_config_add_template('upc_background_measurements', @_);
}


sub upc_background_measurements_create
{
    return any_config_create('upc_background_measurements', @_);
}


sub upc_background_measurements_exists
{
    my $properties = any_config_properties('upc_background_measurements', @_);

    return($properties->{exists});
}


#
# generate a unique measurement definition name
#

sub upc_background_measurements_generate_definition_name
{
    my $measurements = shift;

    my $measurement_name = shift;

    return any_config_entry_generate_definition_name($measurements->{upc_background_measurements}, $measurement_name, 'numeric');
}


#
# generate a unique measurement ID
#

sub upc_background_measurements_generate_next_ID
{
    return any_config_generate_ID('upc_background_measurements', @_);
}


sub upc_background_measurements_read
{
    return any_config_read('upc_background_measurements', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub upc_background_measurements_restore
{
    return any_config_restore('upc_background_measurements', @_);
}


sub upc_background_measurements_write
{
    return any_config_write('upc_background_measurements', 'config', @_);
}


persistency_info_add('upc_background_measurements', $upc_background_measurements_info);


