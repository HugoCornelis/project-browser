#!/usr/bin/perl -w
#
# $Id: Calibration.pm,v 1.2 2005/06/03 15:43:24 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::Calibration;


use strict;


use NTC::Util_a01 'list_is_member';

use Sesa::Persistency qw(
			 any_config_create_sections
			 any_config_get_installed_sections
			 any_config_read
			 any_config_restore
			 any_config_section_name_2_section_keys
			 any_config_write
			 persistency_info_add
			);


require Exporter;


our @ISA = qw(Exporter);

our @EXPORT_OK = qw(
		    calibration_adjust_differences_with_hpa_summary
		    calibration_adjust_differences_with_ucc_summary
		    calibration_apply_hpa_differences
		    calibration_apply_ucc_differences
		    calibration_expand_hpa_summary
		    calibration_expand_ucc_summary
		    fix_calibration_logic
		    read_calibration
		    restore_calibration
		    write_calibration
		   );


my $sems_calib_file = '/var/sems/calibration/calib.txt';


# tags that delimit the individual sections in the calibration file.
# this still has to be expanded, see devices cgis

my $calib_tags
    = {
       'const' => {
		   'keys' => [
			      "## -!- Sems section : const -!-\n",
			      "## -!- Sems section : end const -!-\n"
			     ],
		   'layout' => undef,
		   'required' => 'no',
		  },
       # allows to set permissions on other sections ?
       # in that case, table with other sections.
       'header' => {
		    'keys' => [
			       "## -!- Sems section : header -!-\n",
			       "## -!- Sems section : end header -!-\n"
			      ],
		    'required' => 'no',
		    'shared' => 'global',
		   },
       'hpa-summary' => {
			 'config_keys' => [ 'hpa_summary' ],
			 'keys' => [
				    "## -!- Sems section : hpa-summary -!-\n",
				    "## -!- Sems section : end hpa-summary -!-\n"
				   ],
			 'required' => 'no',
			},
       'hpa-differences' => {
			     'config_keys' => [ 'hpa_differences' ],
			     'keys' => [
					"## -!- Sems section : hpa-differences -!-\n",
					"## -!- Sems section : end hpa-differences -!-\n"
				       ],
			     'required' => 'no',
			    },
       # table with data entries, some in text fields.
       'map' => {
		 'keys' => [
			    "## -!- Sems section : map -!-\n",
			    "## -!- Sems section : end map -!-\n"
			   ],
		 'required' => 'yes',
		},
       # one text field per entry.
       'reflevel' => {
		      'keys' => [
				 "## -!- Sems section : reflevel -!-\n",
				 "## -!- Sems section : end reflevel -!-\n"
				],
		      'required' => 'no',
		     },
       'ucc-summary' => {
			 'config_keys' => [ 'ucc_summary' ],
			 'keys' => [
				    "## -!- Sems section : ucc-summary -!-\n",
				    "## -!- Sems section : end ucc-summary -!-\n"
				   ],
			 'required' => 'no',
			},
       'ucc-differences' => {
			     'config_keys' => [ 'ucc_differences' ],
			     'keys' => [
					"## -!- Sems section : ucc-differences -!-\n",
					"## -!- Sems section : end ucc-differences -!-\n"
				       ],
			     'required' => 'no',
			    },
       # none or read only
       'version' => {
		     'keys' => [
				"## -!- Sems section : version -!-\n",
				"## -!- Sems section : end version -!-\n"
			       ],
		     'required' => 'yes',
		    },
      };

# calibration info table

my $calib_info
    = {
       'filename' => $sems_calib_file,
       'is_valid'
       => sub { return(exists $_[1]->{version} && $_[1]->{version} == 2); },
       'name' => 'calibration',
       'tags' => $calib_tags,
      };


sub calibration_adjust_differences_with_hpa_summary
{
    my $installed_sections = calibration_get_installed_sections();

    if (!list_is_member($installed_sections, 'hpa-summary'))
    {
	# create the hpa-summary if needed

	calibration_create_hpa_summary();
    }

    # adjust differences

    calibration_update_hpa_differences();
}


#
# calibration_adjust_differences_with_ucc_summary()
#
# Update the differences between the expanded calibration table and
# the ucc summary.  If the summary does not exist yet, it is created.
#

sub calibration_adjust_differences_with_ucc_summary
{
    my $installed_sections = calibration_get_installed_sections();

    if (!list_is_member($installed_sections, 'ucc-summary'))
    {
	# create the ucc-summary if needed

	calibration_create_ucc_summary();
    }

    # adjust differences

    calibration_update_ucc_differences();
}


sub calibration_apply_hpa_differences
{
    my $calibration = shift;

    my $hpa_differences = $calibration->{hpa_differences};

    # get mapping of the calibration file and the hpa summary

    my $calibration_mapping = $calibration->{map};

    foreach my $calibration_path (keys %$calibration_mapping)
    {
	# if the path does not exist in the hpa differences

	if (!exists $hpa_differences->{$calibration_path})
	{
	    # return failure

	    return undef;
	}

	# get config for this path from the expanded calibration table

	my $calibration_path_config = $calibration_mapping->{$calibration_path};

	# take differences

	$calibration_path_config->{hpa} -= $hpa_differences->{$calibration_path}->{hpa};
    }

    return $calibration;
}


sub calibration_apply_ucc_differences
{
    my $calibration = shift;

    my $ucc_differences = $calibration->{ucc_differences};

    # get mapping of the calibration file and the ucc summary

    my $calibration_mapping = $calibration->{map};

    foreach my $calibration_path (keys %$calibration_mapping)
    {
	# if the path does not exist in the ucc differences

	if (!exists $ucc_differences->{$calibration_path})
	{
	    # return failure

	    return undef;
	}

	# get config for this path from the expanded calibration table

	my $calibration_path_config = $calibration_mapping->{$calibration_path};

	# take differences

	$calibration_path_config->{ucc} -= $ucc_differences->{$calibration_path}->{ucc};

	$calibration_path_config->{reflevel} -= $ucc_differences->{$calibration_path}->{reflevel};
    }

    return $calibration;
}


#
# calibration_create_hpa_summary()
#
# Create the HPA summary based on the current settings of the
# calibration table.
#
# The summary is based on the gain settings for all HPAs for all
# ports.
#
# This sub makes sense for a limited set of stations only.
#
# If there is no calibration file, this sub will silently fail.
#

sub calibration_create_hpa_summary
{
    my ($calibration, $read_error) = read_calibration();

    if (!$calibration || $read_error)
    {
	return undef;
    }

    # create content for the hpa summary

    my $hpa_summary = {};

    # loop over all paths in the mapping

    my $map = $calibration->{map};

    foreach my $path (keys %$map)
    {
	my $path_config = $map->{$path};

	# extract the hpa from the path

	$path =~ /([^_]*_x.+)$/i;

	my $hpa_path = $1;

	# copy the relevant parameters : hpa attenuation

	#! possibly overwrites previous info

	$hpa_summary->{$hpa_path}->{hpa} = $path_config->{hpa};
    }

    # create the section using that content

    my $config_keys = any_config_section_name_2_section_keys('calibration', 'hpa-summary', );

    if (scalar @$config_keys != 1)
    {
	die "Internal failure: calibration file is configured for multiple or no keys for the hpa-summary, but calibration_create_hpa_summary() only expects one key";
    }

    $calibration->{$config_keys->[0]} = $hpa_summary;

    any_config_create_sections('calibration', [ 'hpa-summary', ], $calibration, );

    any_config_create_sections('calibration', [ 'hpa-differences', ], $calibration, );

    # synchronize the expanded calibration table with the summary

    $calibration = calibration_expand_hpa_summary($calibration);

    # write the expanded table and reflevel section to the file

    write_calibration($calibration, [ 'reflevel', 'map', ], );
}


#
# calibration_create_ucc_summary()
#
# Create the UCC summary based on the current settings of the
# calibration table.
#
# The summary is based on the gain settings for UCC_1 for all ports.
#
# This sub makes sense for a limited set of stations only.
#
# If there is no calibration file, this sub will silently fail.
#

sub calibration_create_ucc_summary
{
    my ($calibration, $read_error) = read_calibration();

    if (!$calibration || $read_error)
    {
	return undef;
    }

    # create content for the ucc summary

    my $ucc_summary = {};

    # we did not visit any port yet

    my $visited_ports = [];

    # loop over all paths in the mapping

    my $map = $calibration->{map};

    foreach my $path (keys %$map)
    {
	my $path_config = $map->{$path};

	# only consider UCC 1

	next if $path !~ /_u1/i;

	# extract the port from the path

	$path =~ /^p(\d+)_/i;

	my $port = $1;

	# compute the reflevel index from the port number

	my $index = $port;

	$index =~ s/^p//;

	# mark the port as visited

	push @$visited_ports, $port;

	# copy the relevant parameters : ucc gain, reflevel and reflevel index

	#! possible loss of information for the other uccs

	$ucc_summary->{$port}->{ucc} = $path_config->{ucc};
	$ucc_summary->{$port}->{reflevel} = $calibration->{reflevel}->{$index} || $calibration->{reflevel}->{1};
	$ucc_summary->{$port}->{reflevel_index} = $index;

# 	$ucc_summary->{$port}->{reflevel} = $path_config->{reflevel};
# 	$ucc_summary->{$port}->{reflevel_index} = $path_config->{reflevel_index};
    }

    # create the section using that content

    my $config_keys = any_config_section_name_2_section_keys('calibration', 'ucc-summary', );

    if (scalar @$config_keys != 1)
    {
	die "Internal failure: calibration file is configured for multiple or no keys for the ucc-summary, but calibration_create_ucc_summary() only expects one key";
    }

    $calibration->{$config_keys->[0]} = $ucc_summary;

    any_config_create_sections('calibration', [ 'ucc-summary', ], $calibration, );

    any_config_create_sections('calibration', [ 'ucc-differences', ], $calibration, );

    # if there are not enough entries in the reference level table for this amount of ports

    my $number_of_reference_levels = scalar keys %{$calibration->{reflevel}};

    my $number_of_ports = scalar @$visited_ports;

    if ($number_of_reference_levels < $number_of_ports)
    {
	my $start_index = $number_of_reference_levels + 1;

	my $end_index = $number_of_ports;

	# create an index in the reference levels for each port

	$calibration->{reflevel}
	    = {
	       %{$calibration->{reflevel}},
	       map
	       {
		   $_ => $calibration->{reflevel}->{1};
	       }
	       $start_index .. $end_index,
	      };
    }

    # synchronize the expanded calibration table with the summary

    $calibration = calibration_expand_ucc_summary($calibration);

    # write the expanded table and reflevel section to the file

    write_calibration($calibration, [ 'reflevel', 'map', ], );
}


#
# calibration_expand_hpa_summary()
#
# Read the calibration file and expand the hpa-summary into the
# calibration table.
#
# Returns the resulting calibration table.
#

sub calibration_expand_hpa_summary
{
    my $result = shift;

    # loop over the hpa paths in the summary

    my $hpa_summary = $result->{hpa_summary};

    foreach my $hpa_path (keys %$hpa_summary)
    {
	# get all settable values

	my $hpa = $hpa_summary->{$hpa_path}->{hpa};

	# loop over all paths

	my $mapping = $result->{map};

	foreach my $path (keys %$mapping)
	{
	    # if the path matches with this hpa path

	    if ($path =~ /${hpa_path}$/)
	    {
		my $path_config = $mapping->{$path};

		# overwrite the current data

		$path_config->{hpa} = $hpa;
	    }
	}
    }

    # return the calibration

    return $result;
}


#
# calibration_expand_ucc_summary()
#
# Read the calibration file and expand the ucc-summary into the
# calibration table.
#
# Returns the resulting calibration table.
#

sub calibration_expand_ucc_summary
{
    my $result = shift;

    # loop over the ports in the summary

    my $ucc_summary = $result->{ucc_summary};

    foreach my $port (keys %$ucc_summary)
    {
	# get index from port number

	my $index = $port;

	$index =~ s/^p//;

	# get all settable values

	my $ucc = $ucc_summary->{$port}->{ucc};
	my $reflevel = $ucc_summary->{$port}->{reflevel};

	# write the reflevel and index into the reflevel section data

	$result->{reflevel}->{$index} = $reflevel;

	# loop over all paths

	my $mapping = $result->{map};

	foreach my $path (keys %$mapping)
	{
	    # if the path matches with this port

	    if ($path =~ /^p${port}_/)
	    {
		my $path_config = $mapping->{$path};

		# overwrite the current data

		$path_config->{ucc} = $ucc;
		$path_config->{reflevel} = $reflevel;
		$path_config->{reflevel_index} = $index;
	    }
	}
    }

    # return the calibration

    return $result;
}


sub calibration_get_installed_sections
{
    return any_config_get_installed_sections('calibration', @_, );
}


#
# calibration_update_hpa_differences()
#
# Compute the differences between the hpa-summary and the calibration
# table and write the differences to the calibration file.
#

sub calibration_update_hpa_differences
{
    # read the calibration

    my ($calibration, $read_error) = read_calibration();

    if (!$calibration || $read_error)
    {
	return undef;
    }

    # expand the hpa summary

    my $hpa_expanded_calibration = calibration_expand_hpa_summary();

    if (!$hpa_expanded_calibration)
    {
	return undef;
    }

    # initialize the differences set

    my $hpa_differences = {};

    # get mapping of the calibration file and the hpa summary

    my $calibration_mapping = $calibration->{map};

    my $hpa_mapping = $hpa_expanded_calibration->{map};

    # loop over all paths in the calibration file

    foreach my $calibration_path (keys %$calibration_mapping)
    {
	# if the path does not exist in the hpa expansion

	if (!exists $hpa_mapping->{$calibration_path})
	{
	    # return failure

	    return undef;
	}

	# get config for this path from the expanded calibration table

	my $calibration_path_config = $calibration_mapping->{$calibration_path};

	# get config for this path from the expanded hpa summary

	my $hpa_summary_path_config = $hpa_mapping->{$calibration_path};

	# take differences

	$hpa_differences->{$calibration_path}->{hpa}
	    = $calibration_path_config->{hpa} - $hpa_summary_path_config->{hpa};
    }

    # fill in the differences

    $calibration->{hpa_differences} = $hpa_differences;

    # write differences

    write_calibration($calibration, [ 'hpa-differences', ], );
}


#
# calibration_update_ucc_differences()
#
# Compute the differences between the ucc-summary and the calibration
# table and write the differences to the calibration file.
#

sub calibration_update_ucc_differences
{
    # read the calibration

    my ($calibration, $read_error) = read_calibration();

    if (!$calibration || $read_error)
    {
	return undef;
    }

    # expand the ucc summary

    my $ucc_expanded_calibration = calibration_expand_ucc_summary();

    if (!$ucc_expanded_calibration)
    {
	return undef;
    }

    # initialize the differences set

    my $ucc_differences = {};

    # get mapping of the calibration file and the ucc summary

    my $calibration_mapping = $calibration->{map};

    my $ucc_mapping = $ucc_expanded_calibration->{map};

    # loop over all paths in the calibration file

    foreach my $calibration_path (keys %$calibration_mapping)
    {
	# if the path does not exist in the ucc expansion

	if (!exists $ucc_mapping->{$calibration_path})
	{
	    # return failure

	    return undef;
	}

	# get config for this path from the expanded calibration table

	my $calibration_path_config = $calibration_mapping->{$calibration_path};

	# get config for this path from the expanded ucc summary

	my $ucc_summary_path_config = $ucc_mapping->{$calibration_path};

	# take differences

	$ucc_differences->{$calibration_path}->{ucc}
	    = $calibration_path_config->{ucc} - $ucc_summary_path_config->{ucc};

	$ucc_differences->{$calibration_path}->{reflevel}
	    = $calibration_path_config->{reflevel} - $ucc_summary_path_config->{reflevel};
    }

    # fill in the differences

    $calibration->{ucc_differences} = $ucc_differences;

    # write differences

    write_calibration($calibration, [ 'ucc-differences', ], );
}


#
# Fix calibration logic after restoring a section (e.g. after recovery from
# factory backup).
#
# Fixing calibration logic means correcting reflevel entries that cannot be
# found in the reflevel table, by replacing their value with a value found in
# the table via the index.
#
# This sub is a bit inconsistent and should be used with care.
#
# $_[0] : ref to array with keys of sections to fix, only one entry allowed
# for the moment, i.e. ['map'] or ['reflevel'].
#

sub fix_calibration_logic
{
    my $keys_set = shift;

    my $fixed_keys = [];

    # restore levels in map

    my $calibration = do $sems_calib_file;

    foreach my $key (@$keys_set)
    {
	if ($key eq 'reflevel')
	{
	    # here we lose entries that did not conform to a reflevel in the
	    # reflevel table.

	    foreach my $path (keys %{$calibration->{map}})
	    {
#		print "<p> fixing logic for $path" ;

		my $reflevel_index
		    = $calibration->{map}->{$path}->{reflevel_index};

		$calibration->{map}->{$path}->{reflevel}
		    = $calibration->{reflevel}->{$reflevel_index};
	    }

	    # remember to rewrite map section

	    push @$fixed_keys, 'map' ;
	}
	elsif ($key eq 'map')
	{
	    # here we loose entries that did not conform to a reflevel in the
	    # reflevel table.

	    foreach my $path (keys %{$calibration->{map}})
	    {
#		print "<p> fixing logic for $path" ;

		my $reflevel_index
		    = $calibration->{map}->{$path}->{reflevel_index};

		$calibration->{map}->{$path}->{reflevel}
		    = $calibration->{reflevel}->{$reflevel_index};
	    }

	    # remember to rewrite map section

	    push @$fixed_keys, 'map' ;
	}
    }

    # write calibration with fixed logic

    write_calibration($calibration, $fixed_keys);
}


# # obsolete

# sub get_calibration_varname
# {

#     $_ = file2str($sems_calib_file);

#     m/^## sems_variable_name %([^\n]*)/m ;

#     return $1;
# }


sub read_calibration
{
    return any_config_read('calibration', @_);
}


# You must first check with read_calibration() to check if the calibration
# file is ok before calling this function.

sub restore_calibration
{
    return any_config_restore('calibration', @_);
}


sub write_calibration
{
    return any_config_write('calibration', 'config', @_);
}


sub write_calibration_factory
{
    return any_config_write('calibration', 'factory', @_);
}


persistency_info_add('calibration', $calib_info);


