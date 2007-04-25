#!/usr/bin/perl -w
#
# $Id: Ideas_RFPortMapping.pm,v 1.2 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::Ideas_RFPortMapping;


use strict;


use Sesa::Persistency qw(
			 any_config_read
			 any_config_restore
			 any_config_write
			 persistency_info_add
			);


require Exporter;


our @ISA = qw(Exporter);

our @EXPORT_OK = qw(
		    read_ideas_rf_port_mapping
		    restore_ideas_rf_port_mapping
		    write_ideas_rf_port_mapping
		   );


my $ideas_rf_port_mapping = '/var/sems/rf_port_mapping';


my $ideas_rf_port_mapping_tags
    = {
       'configuration' => {
			   'keys' => [
				      "## -!- Sems section : rf-port-mapping-configuration -!-\n",
				      "## -!- Sems section : end rf-port-mapping-configuration -!-\n"
				     ],
			   'required' => 'yes',
			  },
       'downlink_port_mapping' => {
				   'keys' => [
					      "## -!- Sems section : downlink-port-mapping -!-\n",
					      "## -!- Sems section : end downlink-port-mapping -!-\n"
					     ],
				   'required' => 'yes',
				  },
       'uplink_port_mapping' => {
				 'keys' => [
					    "## -!- Sems section : uplink-port-mapping -!-\n",
					    "## -!- Sems section : end uplink-port-mapping -!-\n"
					   ],
				 'required' => 'yes',
				},
       # none or read only
       'rf_port_mapping_version' => {
				    'keys' => [
					       "## -!- Sems section : rf-port-mapping-version -!-\n",
					       "## -!- Sems section : end rf-port-mapping-version -!-\n"
					      ],
				    'required' => 'yes',
				   },
      };

# ideas_rf_port_mapping info table

my $ideas_rf_port_mapping_info
    = {
       'filename' => $ideas_rf_port_mapping,
       'is_valid'
       => sub { return(exists $_[1]->{rf_port_mapping_version} && $_[1]->{rf_port_mapping_version} == 1); },
       'name' => 'ideas_rf_port_mapping',
       'tags' => $ideas_rf_port_mapping_tags,
      };


sub read_ideas_rf_port_mapping
{
    return any_config_read('ideas_rf_port_mapping', @_);
}


# You must first check with read_rf_port_mapping() to check if the config file
# is ok before calling this function.

sub restore_ideas_rf_port_mapping
{
    return any_config_restore('ideas_rf_port_mapping', @_);
}


sub write_ideas_rf_port_mapping
{
    return any_config_write('ideas_rf_port_mapping', 'config', @_);
}


sub write_ideas_rf_port_mapping_factory
{
    return any_config_write('ideas_rf_port_mapping', 'factory', @_);
}


persistency_info_add('ideas_rf_port_mapping', $ideas_rf_port_mapping_info);


