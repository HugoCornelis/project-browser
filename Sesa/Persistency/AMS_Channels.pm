#!/usr/bin/perl -w
#
# $Id: AMS_Channels.pm,v 1.2 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::AMS_Channels;


use strict;


use Sesa::Persistency qw(
			 any_config_add_template
			 any_config_create
			 any_config_entry_generate_definition_name
			 any_config_properties
			 any_config_read
			 any_config_restore
			 any_config_write
			 persistency_info_add
			);


require Exporter;


our @ISA = qw(Exporter);

our @EXPORT_OK = qw(
		    channel_database_add_template
		    channel_database_create
		    channel_database_exists
		    channel_database_generate_definition_name
		    channel_database_read
		    channel_database_restore
		    channel_database_write
		   );


my $channel_database_file = '/var/sems/channel_database';


# channel default values.

my $add_channel_defaults
    = {
       "Channel Name" => 'NEW_NAME',
       ChannelCoPol => '',
       ChannelSpotBeam => '',
       ChannelSymbolRate => 128000,
       CopolCarrierSpec => 6,
       CopolDetectionLimit => 2,
       CopolFreqSpec => 50000,
       CopolLO => 10000008000,
       CopolRegrowthSpec => 20,
       CopolRfPort => '',
       CopolRxFreq => 11080000000,
       CopolTxFreq => '',
       XpolAvailable => 1,
       XpolDiscrimSpec => 25,
       XpolLO => 10000000000,
       XpolRfPort => 2,
      };

# tags that delimit the individual sections in the config file.

my $channel_database_tags
    = {
       'channel-definitions' => {
				 'config_keys' => [ 'channel_definitions', ],
				 'keys' => [
					    "## -!- Sems section : channel-definitions -!-\n",
					    "## -!- Sems section : end channel-definitions -!-\n"
					   ],
				 'required' => 'yes',
				 'add_template' => {
						    'values' => $add_channel_defaults,
						    'rewriters' => {
								    'NEW_NAME' => \&channel_database_generate_definition_name,
								   },
						   },
				},
       'channel-key-descriptions' => {
				      'config_keys' => [ 'key_descriptions', ],
				      'keys' => [
						 "## -!- Sems section : channel-key-descriptions -!-\n",
						 "## -!- Sems section : end channel-key-descriptions -!-\n"
						],
				      'required' => 'no',
# 				      'add_template' => {
# 							 'values' => $add_channel_defaults,
# 							 'rewriters' => {
# 									 'NEW_NAME' => \&channel_database_generate_definition_name,
# 									},
# 							},
				     },
      };

# channel database template

my $channel_database_template ='#  Channel database file for Newtec SEMS
# $Id: AMS_Channels.pm,v 1.2 2005/06/03 15:43:24 hco Exp $
#
## ===========================================================
## -!- Sems section : header -!-
## sems_variable_name %channels
## -!- Sems section : end header -!-
## ===========================================================

my %channels;


## ===========================================================
## -!- Sems section : channel-definitions -!-

$channels{channel_definitions}
    = {
      };

## -!- Sems section : end channel-definitions -!-
## ===========================================================

return \%channels;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## End:
';


# channel database info table

my $channel_database_info
    = {
       'name' => 'channel_database',
       'filename' => $channel_database_file,
       'is_valid' => undef,
       'tags' => $channel_database_tags,
       'template_string' => $channel_database_template,
      };


sub channel_database_add_template
{
    return any_config_add_template('channel_database', @_);
}


sub channel_database_create
{
    return any_config_create('channel_database', @_);
}


sub channel_database_exists
{
    my $properties = any_config_properties('channel_database', @_);

    return($properties->{exists});
}


#
# generate a unique channel definition name for the channel database
#

sub channel_database_generate_definition_name
{
    my $channels = shift;

    my $channel_name = shift;

    return any_config_entry_generate_definition_name($channels->{channel_definitions}, $channel_name, 'numeric');
}


sub channel_database_read
{
    return any_config_read('channel_database', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub channel_database_restore
{
    return any_config_restore('channel_database', @_);
}


sub channel_database_write
{
    return any_config_write('channel_database', 'config', @_);
}


persistency_info_add('channel_database', $channel_database_info);


