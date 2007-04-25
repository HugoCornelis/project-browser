#!/usr/bin/perl -w
#
# $Id: SemsConfig.pm,v 1.2 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::SemsConfig;


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
		    read_sems_config
		    restore_sems_config
		    write_sems_config
		   );


my $sems_config_file = '/var/sems/sems.config';


# tags that delimit the individual sections in the config file.

my $config_tags
    = {
       'eirp_constant' => {
			   'keys' => [
				      "## -!- Sems section : eirp_constant -!-\n",
				      "## -!- Sems section : end eirp_constant -!-\n"
				     ],
			   'required' => 'no',
			  },
       'channels' => {
		      'keys' => [
				 "## -!- Sems section : channels -!-\n",
				 "## -!- Sems section : end channels -!-\n"
				],
		      'required' => 'no',
		     },
       'devices' => {
		     'keys' => [
				"## -!- Sems section : devices -!-\n",
				"## -!- Sems section : end devices -!-\n"
			       ],
		     'required' => 'no',
		    },
       'ideas-sems-config' => {
			       'config_keys' => [ 'enable_subsys', ],
			       'keys' => [
					  "## -!- Sems section : ideas-sems-config -!-\n",
					  "## -!- Sems section : end ideas-sems-config -!-\n"
					 ],
			       'required' => 'no',
			      },
       'serial-devices'
       => {
	   'config_keys' => [ 'devices', ],
	   'export_filter' =>
	   sub
	   {
	       exists $_[0]->{bus}
		   and $_[0]->{bus} =~ m/^ntc[0-9]+/;
	   },
	   'keys' => [
		      "## -!- Sems section : serial devices -!-\n",
		      "## -!- Sems section : end serial devices -!-\n"
		     ],
	   'required' => 'no',
	  },
       'tcp-devices'
       => {
	   'config_keys' => [ 'devices', ],
	   'export_filter' =>
	   sub
	   {
	       exists $_[0]->{bus}
		   and $_[0]->{bus} =~ m/^localhost:[0-9]+/;
	   },
	   'keys' => [
		      "## -!- Sems section : TCP devices -!-\n",
		      "## -!- Sems section : end TCP devices -!-\n"
		     ],
	   'required' => 'no',
	  },
       'rmcp-tcp-devices'
       => {
	   'config_keys' => [ 'devices', ],
	   'export_filter' =>
	   sub
	   {
	       exists $_[0]->{protocol}
		   and $_[0]->{protocol} eq 'rmcp_TCP01';
	   },
	   'keys' => [
		      "## -!- Sems section : RMCP TCP devices -!-\n",
		      "## -!- Sems section : end RMCP TCP devices -!-\n"
		     ],
	   'required' => 'no',
	  },
       'GUI' => {
		 'keys' => [
			    "## -!- Sems section : GUI -!-\n",
			    "## -!- Sems section : end GUI -!-\n"
			   ],
		 'required' => 'no',
		},
       'header' => {
		    'keys' => [
			       "## -!- Sems section : header -!-\n",
			       "## -!- Sems section : end header -!-\n"
			      ],
		    'required' => 'no',
		    'shared' => 'global',
		   },
       'init' => {
		  'keys' => [
			     "## -!- Sems section : init -!-\n",
			     "## -!- Sems section : end init -!-\n"
			    ],
		  'required' => 'no',
		 },
       'network' => {
		     'keys' => [
				"## -!- Sems section : network -!-\n",
				"## -!- Sems section : end network -!-\n"
			       ],
		     'required' => 'no',
		    },
       'packages' => {
		      'config_keys' => [ 'sems_sw_packages', ],
		      'keys' => [
				 "## -!- Sems section : packages -!-\n",
				 "## -!- Sems section : end packages -!-\n"
				],
		      'required' => 'no',
		     },
       'system' => {
		    'config_keys' => [
				      'site_file_name',
				      'site_full_name',
				      'build_cvs_tag',
				      'time_zone',
				      'license',
				      'uii_port',
				      'uiixml',
				      'has_sessions',
				      'save_sessions',
				      'audible_alarm',
				      'enable_agent_indexing',
				     ],
		    'keys' => [
			       "## -!- Sems section : system -!-\n",
			       "## -!- Sems section : end system -!-\n"
			      ],
		    'required' => 'yes',
		   },
      };

# config info table

my $config_info
    = {
       'name' => 'config',
       'filename' => $sems_config_file,
       'is_valid' => undef,
       'tags' => $config_tags,
      };


sub read_sems_config
{
    return any_config_read('config', @_);
}


# You must first check with read_sems_config() to check if the config file is
# ok before calling this function.

sub restore_sems_config
{
    return any_config_restore('config', @_);
}


sub write_sems_config
{
    return any_config_write('config', 'config', @_);
}


sub write_sems_config_factory
{
    return any_config_write('config', 'factory', @_);
}


persistency_info_add('config', $config_info);


