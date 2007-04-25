#!/usr/bin/perl -w
#
# $Id: Ideas_FrequencyPlan.pm,v 1.2 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::Ideas_FrequencyPlan;


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
		    read_ideas_frequency_plan
		    restore_ideas_frequency_plan
		    write_ideas_frequency_plan
		   );


my $ideas_frequency_plan = '/var/sems/frequency_plan';


my $ideas_frequency_plan_tags
    = {
       'downlink_frequencies' => {
				  'keys' => [
					     "## -!- Sems section : downlink-frequencies -!-\n",
					     "## -!- Sems section : end downlink-frequencies -!-\n"
					    ],
				  'required' => 'yes',
				 },
       'uplink_frequencies' => {
				'keys' => [
					   "## -!- Sems section : uplink-frequencies -!-\n",
					   "## -!- Sems section : end uplink-frequencies -!-\n"
					  ],
				'required' => 'yes',
			       },
       # none or read only
       'frequency_plan_version' => {
				    'keys' => [
					       "## -!- Sems section : frequency-plan-version -!-\n",
					       "## -!- Sems section : end frequency-plan-version -!-\n"
					      ],
				    'required' => 'yes',
				   },
      };

# ideas_frequency_plan info table

my $ideas_frequency_plan_info
    = {
       'filename' => $ideas_frequency_plan,
       'is_valid'
       => sub { return(exists $_[1]->{frequency_plan_version} && $_[1]->{frequency_plan_version} == 1); },
       'name' => 'ideas_frequency_plan',
       'tags' => $ideas_frequency_plan_tags,
      };


sub read_ideas_frequency_plan
{
    return any_config_read('ideas_frequency_plan', @_);
}


# You must first check with read_frequency_plan() to check if the config file
# is ok before calling this function.

sub restore_ideas_frequency_plan
{
    return any_config_restore('ideas_frequency_plan', @_);
}


sub write_ideas_frequency_plan
{
    return any_config_write('ideas_frequency_plan', 'config', @_);
}


persistency_info_add('ideas_frequency_plan', $ideas_frequency_plan_info);


