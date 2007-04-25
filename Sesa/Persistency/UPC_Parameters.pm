#!/usr/bin/perl -w
#
# $Id: UPC_Parameters.pm,v 1.3 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::UPC_Parameters;


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
		    upc_parameters_add_template
		    upc_parameters_create
		    upc_parameters_exists
		    upc_parameters_generate_definition_name
		    upc_parameters_generate_next_ID
		    upc_parameters_read
		    upc_parameters_restore
		    upc_parameters_write
		   );


my $upc_parameters_file = '/var/sems/upc/parameters';


# tags that delimit the individual sections in the config file.

my $upc_parameters_tags
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
       'upc-controlled-devices' => {
				    'config_keys' => [
						      'upc_controlled_devices',
						     ],
				    'keys' => [
					       "## -!- Sems section : upc-controlled-devices -!-\n",
					       "## -!- Sems section : end upc-controlled-devices -!-\n",
					      ],
				    'required' => 'yes',
				   },
       'upc-parameters' => {
			    'config_keys' => [
					      'upc_parameters',
					     ],
			    'keys' => [
				       "## -!- Sems section : upc-parameters -!-\n",
				       "## -!- Sems section : end upc-parameters -!-\n",
				      ],
			    'required' => 'yes',
			   },
       'upc-parameters-version' => {
				    'config_keys' => [ 'upc_parameters_version', ],
				    'keys' => [
					       "## -!- Sems section : upc-parameters-version -!-\n",
					       "## -!- Sems section : end upc-parameters-version -!-\n",
					      ],
				    'required' => 'yes',
				   },
       'upc-validator-devices' => {
				    'config_keys' => [
						      'upc_validator_devices',
						     ],
				    'keys' => [
					       "## -!- Sems section : upc-validator-devices -!-\n",
					       "## -!- Sems section : end upc-validator-devices -!-\n",
					      ],
				    'required' => 'yes',
				   },
      };

# UPC parameterss template

my $upc_parameters_template ='#  UPC Parameters file for Newtec SEMS
# $Id: UPC_Parameters.pm,v 1.3 2005/06/03 15:43:24 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %parameters
## -!- Sems section : end header -!-
## ===========================================================

my %parameters;


## ===========================================================
## -!- Sems section : upc-parameters-version -!-

$parameters{upc_parameters_version}
    = 1;

## -!- Sems section : end upc-parameters-version -!-
## ===========================================================


## ===========================================================
## -!- Sems section : modification-info -!-

$parameters{modification_info}
    = {
       user => "USER_NAME",
       date => "DATE",
       count => 0,
      };

## -!- Sems section : end modification-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : creation-info -!-

$parameters{creation_info}
    = {
       user => "USER_NAME",
       date => "DATE",
      };

## -!- Sems section : end creation-info -!-
## ===========================================================


## ===========================================================
## -!- Sems section : upc-parameters -!-

$parameters{upc_parameters}
    = {
       ntcSeEqUPCHPAPsat => 55,
       ntcSeEqUPCHPAOutputBackOff => 5,
       ntcSeEqUPCMaximalCorrection => 5,
       ntcSeEqUPCNumberOfSamples => 7,
       ntcSeEqUPCClearSkyBeaconReceptionStrength => "TBD",
       ntcSeEqUPCProportionality => 1.7,
       ntcSeEqUPCMinimalStepSize => 1,
       ntcSeEqUPCMaximalStepSize => 2,
       ntcSeEqUPCPMaxAccuracy => 0.5,
      };

## -!- Sems section : end upc-parameters -!-
## ===========================================================

## ===========================================================
## -!- Sems section : upc-controlled-devices -!-

$parameters{upc_controlled_devices}
    = {
       ntcSeEqUPCListOfControlledDevices => {},
      };

## -!- Sems section : end upc-controlled-devices -!-
## ===========================================================

## ===========================================================
## -!- Sems section : upc-validator-devices -!-

$parameters{upc_validator_devices}
    = {
       ntcSeEqUPCListOfValidatorDevices => {},
      };

## -!- Sems section : end upc-validator-devices -!-
## ===========================================================

return \%parameters;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';

# $parameters{upc_parameters}
#     = {
#        ntcSeEqUPCHPANominalAtt => -12,
#        ntcSeEqUPCHPAPsat => 0,
#        ntcSeEqUPCHPAOutputBackOff => 5,
#        ntcSeEqUPCMaximalCorrection => 3,
#        ntcSeEqUPCNumberOfSamples => 3,
#        ntcSeEqUPCClearSkyBeaconReceptionStrength => 0,
#        ntcSeEqUPCProportionality => 1.7,
#        ntcSeEqUPCMinimalStepSize => 0,
#        ntcSeEqUPCMaximalStepSize => 0,
#        ntcSeEqUPCPMaxAccuracy => 3,
#       };


# UPC parameterss info table

my $upc_parameters_info
    = {
       'name' => 'upc_parameters',
       'filename' => $upc_parameters_file,
       'is_valid'
       => sub { return(exists $_[1]->{upc_parameters_version} && $_[1]->{upc_parameters_version} == 1); },
       'tags' => $upc_parameters_tags,
       'template_string' => $upc_parameters_template,
      };


sub upc_parameters_add_template
{
    return any_config_add_template('upc_parameters', @_);
}


sub upc_parameters_create
{
    return any_config_create('upc_parameters', @_);
}


sub upc_parameters_exists
{
    my $properties = any_config_properties('upc_parameters', @_);

    return($properties->{exists});
}


#
# generate a unique measurement definition name
#

sub upc_parameters_generate_definition_name
{
    my $measurements = shift;

    my $measurement_name = shift;

    return any_config_entry_generate_definition_name($measurements->{upc_parameters}, $measurement_name, 'numeric');
}


#
# generate a unique measurement ID
#

sub upc_parameters_generate_next_ID
{
    return any_config_generate_ID('upc_parameters', @_);
}


sub upc_parameters_read
{
    return any_config_read('upc_parameters', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub upc_parameters_restore
{
    return any_config_restore('upc_parameters', @_);
}


sub upc_parameters_write
{
    return any_config_write('upc_parameters', 'config', @_);
}


persistency_info_add('upc_parameters', $upc_parameters_info);


