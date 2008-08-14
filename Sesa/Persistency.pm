#!/usr/bin/perl -w
#
# $Id: Persistency.pm,v 1.9 2005/09/06 11:00:15 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency;


#
# How to add a new config file ?
#
# 1. Add the necessary information to the config file database.
#
# 1.a. Define the appropriate tags.
#
# 1.b. Define the filename.
#
# 1.c. Add the new data to the global config file database.
#
# 2. Define reader/writer subs :
#
# 2.a. for read config.
#
# 2.b. for write config.
#
# 2.c. for restore config.
#
# 2.d. for factory write config.
#
# These subs are normally only frontends for the low-level subs they should
# call.  Export only the high-level ones, i.e. the ones you have defined.
# Next, implement Sesa modules for the new config file, read the comments in 
# sesa/target_install_packages/sesa.
#


use strict;


#t need this one for appropriate error messages.

my $sems_config_file = "/var/sems/sems.config";


#<--- -*- mmm-classes:html-js -*- --->


our $stderr_logging = 0;

BEGIN
{
    $stderr_logging = 0;

    # param list can be array or ref ro array
    sub array_max {
	my ($first, @list) = @_;
	if (ref $first) {
	    @list = @$first;
	} else {
	    unshift @list, $first;
	}
	my $max;
	foreach (@list) {
	    $max = $_ if ! defined $max or $max < $_;
	}
	return $max;
    }


    sub import
    {
	# check if stderr_logging is imported.

	my $count = -1;

	my $index = array_max map { $count++; /^STDERR_LOGGING$/ ? $count : -1 } @_;

	# if stderr_logging is imported

	if ($index ne -1)
	{
	    # remove it from the list to import.

	    splice @_, $index, 1;

	    # and enable stderr_logging

	    $stderr_logging = 1;
	}

	Sesa::Persistency->export_to_level(1, @_);

# 	# configure the package, with possible logging

# 	configure();
    }
}


use Data::Dumper;


# ======================================================================
sub clean_dump {			# varname_base part
    my ($varname_base, $part, %options) = @_;
    my ($purity, $indent, $quotekeys, $sortkeys, $varname)
	= ($Data::Dumper::Purity,
	   $Data::Dumper::Indent,
	   $Data::Dumper::Quotekeys,
	   $Data::Dumper::Sortkeys,
	   $Data::Dumper::Varname);

    $Data::Dumper::Purity    = 1;
    $Data::Dumper::Indent    = 2;
    $Data::Dumper::Quotekeys = 0;
    $Data::Dumper::Sortkeys  = $options{sort} || 1;
    $Data::Dumper::Varname   = $varname_base || 'aaa7bbbb';

    my $dmp = Dumper $part;

    $dmp =~ s/\$$Data::Dumper::Varname.\s*=\s+/   /sg
      unless $varname_base;
    $dmp =~ s/^         //gm;
    $dmp =~ s/[;\n\s]+\Z/;\n/s;
    $dmp =~ s/'([-+]?[1-9]\d*)'/$1/sg;	# intergers not in quotes (take care
                                        # of strings like 0007)
    $dmp =~ s/'0'/0/gs;			# dumper places 0s in quotes. why?

    $Data::Dumper::Purity = $purity;
    $Data::Dumper::Indent = $indent;
    $Data::Dumper::Quotekeys = $quotekeys;
    $Data::Dumper::Sortkeys = $sortkeys;
    $Data::Dumper::Varname = $varname;

    return $dmp;
}


require Exporter;


our @ISA = qw(Exporter);

our @EXPORT_OK = qw(
		    any_config_add_template
		    any_config_create
		    any_config_create_sections
		    any_config_entry_generate_definition_name
		    any_config_generate_ID
		    any_config_get_installed_sections
		    any_config_properties
		    any_config_read
		    any_config_restore
		    any_config_section_name_2_section_keys
		    any_config_specification
		    any_config_write
		    persistency_info_add
		    persistency_info_exists
		   );


my $all_configs
    = {
      };


sub persistency_info_add
{
    my $config_name = shift;

    my $config_info = shift;

    # persistency info must not yet exist

    if (persistency_info_exists($config_name))
    {
	return 0;
    }

    # add the config info to the persistency configuration

    $all_configs->{$config_name} = $config_info;

    # create tag2config info

    if (!persistency_info_create_tag_2_config())
    {
	return 0;
    }

    # check consistency of the mapping

    if (!persistency_info_check_consistency())
    {
	return 0;
    }

    return 1;
}


sub persistency_info_exists
{
    my $config_name = shift;

    if (exists $all_configs->{$config_name})
    {
	return 1;
    }
    else
    {
	return '';
    }
}


#
# Given a tag of a config file, convert to the config name.  Note that
# below, there is a check for uniqueness.  Some of the tags are
# excluded from this mapping meaning that they are shared.
#

my $tag2config;

sub persistency_info_create_tag_2_config
{
    $tag2config
	= {
	   # construct list of config names.

	   map
	   {
	       my $config_name = $_;

	       # construct mapping of tag to config name.

	       map
	       {
		   # map a single tag to its config name.

		   ($_ ne 'header' ? ($_ => $config_name) : ()),;
	       }
		   keys %{$all_configs->{$_}->{tags}};
	   }
	   keys %$all_configs,
	  };

    return 1;
}


sub persistency_info_check_consistency
{
    {
	my $config_tags = {};

	# loop over all registered configs

	while (my ($config_name, $config) = each %$all_configs)
	{
	    # loop over all tags for this config

	    my $tags = $config->{tags};

	    foreach my $tag (keys %$tags)
	    {
		# if the tag is shared

		if ($tags->{$tag}->{shared})
		{
		    # check if all configs register this tag as shared

		    if ($config_tags->{$tag}
			&& ref($config_tags->{$tag}) ne 'ARRAY')
		    {
			die "Invalid specification for tag $tag";
		    }

		    # keep the list of modules sharing this tag

		    push @{$config_tags->{$tag}}, { $config_name => 'shared', };

		    push @{$config_tags->{$tag}}, $config_name;
		}
		else
		{
		    # if this tag is used by two different modules

		    if (exists $config_tags->{$tag}
		        && $config_tags->{$tag} ne $config_name)
		    {
			# error

			die "Config tag $tag is defined by $config_name and $config_tags->{$tag}";
		    }

		    # register the module using this tag

		    $config_tags->{$tag} = $config_name;
		}
	    }
	}

	if ($stderr_logging)
	{
	    print STDERR "Sesa consistency of descriptors :\n", Dumper($config_tags);
	}
    }

    if ($stderr_logging)
    {
	print STDERR "Known Sesa config tags :\n", Dumper($tag2config);
    }

    return 1;
}


#
# any_config_add_template()
#
# Add an entry with default values to a config section.
#
# Returns a hash reference with default values.
#

sub any_config_add_template
{
    my $config = shift;

    my $section = shift;

    # get current content of the database

    my $content = shift;

    # get optional prefix for name

    my $prefix = shift;

    # fetch the add template

    my $add_template = $all_configs->{$config}->{tags}->{$section}->{add_template};

    # fetch all default values.

    my $values = $add_template->{values};

    # copy to result

    my $result = { %$values, };

    # fetch the rewriter code.

    my $rewriters = $add_template->{rewriters};

    # for a hash of default values only

    if (ref $values eq 'HASH')
    {
	# loop over all the default values

	while (my ($entry, $value) = each %$values)
	{
	    # if a rewriter exists

	    if (exists $rewriters->{$value})
	    {
		# call the rewriter to fill in a new value

		$result->{$entry} = &{$rewriters->{$value}}($content, $prefix, );
	    }
	}
    }
    else
    {
	die 'attempt to create default values for an non-hash data structure';
    }

    # return result

    return $result;
}


#
# create an empty config database from the template
#

sub any_config_create
{
#     my $errors = FileHandle->new(">/tmp/errors.txt");

#     print $errors "any_config_create()\n";

    # type of file

    my $type = shift;

    any_config_create_directories($type);

    my $config = $all_configs->{$type};

    my $filename = $config->{filename};

    # produce initial content for the file

    my $content = $config->{template_string};

    my $date = localtime(time());

    my $webmin_user = 'not implemented yet';

#     print $errors "Placing initial values\n";

    $content =~ s/DATE/$date/g;

    $content =~ s/USER_NAME/$webmin_user/g;

    # serialize

#     print $errors "for $filename :\n";

#     print $errors "$content\n";

    my $file = FileHandle->new(">$filename");

    print $file $content;

    $file->close();

    any_config_set_owner('sems', $filename);

#     $errors->close();

    return 1;
}


sub any_config_create_directories
{
    my $type = shift;

    my $config = $all_configs->{$type};

    my $filename = $config->{filename};

    $filename =~ m|(.*)/|;

    my $directories = $1;

    # if we are running as superuser

    #! we can get here from within Sems on a development machine (UID HCO, BBA etc.)
    #! from within Sems on a target machine (UID sems)
    #! or from Sesa (UID root).

    if ($< eq 0)
    {
	# for superuser : create directories and make the accessible for others.

	`sudo mkdir -p "$directories"`;

	`sudo chown sems:tech "$directories"`;
    }
    else
    {
	# for a regular user : create the directories.

	`mkdir -p "$directories"`;
    }
}


#
# any_config_create_sections()
#
# Create a new section in a configuration file.
#
# Works by adding this section at the far end of the file.
#
# Returns success of operation.
#

sub any_config_create_sections
{
    my $type = shift;

    my $config = $all_configs->{$type};

    my $sections = shift;

    my $content = shift;

    # default result : failure

    my $result = 0;

    # read content text from the the file

    my $filename = $config->{filename};

    my $content_text = `cat $filename`;

    my $varname = any_config_get_varname($filename);

    # check if there is a return statement

    if ($content_text =~ /^return.+$varname;$/m)
    {
	# first we add two newlines in front of the varname if they are not there yet

	$content_text =~ s/\n*return(.+)$varname;$/\n\n\nreturn$1$varname;/m;
    }

    if ($content_text =~ /^return.*$varname;$/m)
    {
	# loop over all new sections

	foreach my $section_name (@$sections)
	{
	    # construct the tags for the given section

	    my $tags = $config->{tags}->{$section_name}->{keys};

	    my $start_tag = $tags->[0];
	    my $end_tag = $tags->[1];

	    $start_tag =~ /^(.)/;

	    my $comment_marker = $1;

	    my $start_separator = $comment_marker x 2 . " " . "=" x 59;
	    my $end_separator = $comment_marker x 2 . " " . "=" x 59;

	    my $replacement
		= "$start_separator\n"
		    . "$start_tag"
			. "\n\n"
			    . "$end_tag"
				. "$end_separator\n";

	    $content_text =~ s/\n*return(.+)$varname;$/\n$replacement\n\nreturn$1$varname;/m;

	    # write the file with the new tags

	    str2file($content_text, $filename);
	}

	# write the data into the tagged space

	any_config_write($type, 'config', $content, $sections, );

	# set result : ok

	$result = 1;
    }

    return $result;
}


sub any_config_entry_generate_definition_name
{
    my $config_entry = shift;

    my $definition_name = shift;

    # method must be 'numeric' for the moment.

    my $method = shift;

    # check for duplicates, rename if necessary

    while (exists $config_entry->{$definition_name})
    {
	if ($definition_name =~ /-([0-9]*)$/)
	{
	    my $count = $1 + 1;
	    $definition_name =~ s/-([0-9]*)$/-$count/;
	}
	else
	{
	    $definition_name .= '-1';
	}
    }

    return $definition_name;
}


#t
#t For this sub to work accurately, it is of major importance that
#t the config files are locked correctly.
#t

sub any_config_generate_ID
{
    my $type = shift;

    # old_content should be synchronized with the real content, read below.

    my $old_content = shift;

    # prefix left over from channel database

    my $prefix = shift;

    # get file config

    my $config = $all_configs->{$type};

    # obtain the next id to be used

    my $filename = $config->{filename};

    my $content = do $filename;

    my $next_id_section = $config->{next_id_section};

    my $next_id_entry = section_resolve_to_singleton_entry($config, $next_id_section, );

    my $next_id = $content->{$next_id_entry};

    # set the result : next id to be used

    my $result = $next_id;

    # register the allocation of this id

    $next_id++;

    # serialize the data to the correct config entry in the file

    $content->{$next_id_entry} = $next_id;

    any_config_write($type, 'config', $content, [ $next_id_section, ], );

    # return the allocated id

    return $result;
}


#
# any_config_get_installed_sections()
#
# Given a config file type, check what section are currently installed
# for that file.
#

sub any_config_get_installed_sections
{
    my $type = shift;

    my $config = $all_configs->{$type};

    my $filename = $config->{filename};

    my $context_text = `cat $filename`;

    my $config_tags = $config->{tags};

    my $result = [];

    # loop over all sections known for this config file

    foreach my $config_section (keys %$config_tags)
    {
	# get start and end tag for this section

	my $start_tag = $config_tags->{$config_section}->{keys}->[0];
	my $end_tag = $config_tags->{$config_section}->{keys}->[1];

	# if these tags are found in the file

	if ($context_text =~ /$start_tag/
	    && $context_text =~ /$end_tag/)
	{
	    # add the section name to the result

	    push @$result, $config_section;
	}
    }

    # return result

    return $result;
}


#t
#t what is the status of the following sub : config-type, config or
#t section related ?
#t

sub section_resolve_to_singleton_entry
{
    my $config = shift;

    my $section_name = shift;

    my $config_keys = $config->{tags}->{$section_name}->{config_keys};

    # config keys must exist

    if (!$config_keys)
    {
	return undef;
    }

    # config keys must be singleton

    if (scalar @$config_keys ne 1)
    {
	return undef;
    }

    # return element of singleton

    my $result = $config_keys->[0];

    return $result;
}


# # obsolete

# #
# # Given a config file type and a section, figure out what type of document
# # layout the config file prefers.
# #

# sub any_config_get_section_type
# {
#     # type of file

#     my $type = shift;

#     my $section = shift;

#     # read in config file.

#     my $config = $all_configs->{$type};

#     my $filename = $config->{filename};

#     print STDERR "Reading file $type, $section -> $filename\n";

#     $_ = file2str($filename);

#     # construct a matcher : as close as possible to the opening tag, starts
#     # with the perl 'use' keyword.  the type is everything uptill, but not
#     # including the terminating ';'.

#     my $matcher
# 	= $config->{tags}->{$section}->{keys}->[0]
# 	    . '.*?use ([^;]*);';

#     # if a match has been found

#     my $matched = m/$matcher/m ;

#     if ($matched)
#     {
# 	# return the type.

# 	return $1;
#     }

#     # else

#     else
#     {
# 	# return no type found.

# 	return undef;
#     }
# }


sub any_config_get_varname
{
    my $filename = shift;

    $_ = file2str($filename);

    m/^## sems_variable_name %([^\n]*)/m ;

    return $1;
}


sub any_config_section_name_2_section_keys
{
    my $type = shift;

    my $config = $all_configs->{$type};

    my $section_name = shift;

    my $result = $config->{tags}->{$section_name}->{config_keys};

    return $result;
}


#
# Given a config type, check the properties of the associated resources.
# Mostly these resources consist of a single file.
#

sub any_config_properties
{
    #t use 'stat' and its '_' filehandle ?

    # type of file

    my $type = shift;

    my $config = $all_configs->{$type};

    my $filename = $config->{filename};

    if ($stderr_logging)
    {
	print STDERR "Checking properties of $filename\n";
    }

    my $result = {};

    $result->{filename} = $filename;

    $result->{exists} = -e $filename || 0;
    $result->{readable} = -r $filename || 0;
    $result->{writable} = -w $filename || 0;

    if ($stderr_logging)
    {
	print STDERR "Properties for $filename\n", Dumper($result);
    }

    return($result);
}


sub any_config_read
{
    # type of file

    my $type = shift;

    my $config = $all_configs->{$type};

    my $filename = $config->{filename};

    create_factory_backup($filename);

    if ($stderr_logging)
    {
	print STDERR "Created factory backup for $filename\n";
    }

    if (!-e $filename)
    {
	my $sems_config = do $sems_config_file;

	my $read_error = <<EOF;
  <body>
    <h1>Error</h1>
    Error : '$filename' does not exist.
    <hr>
    <address><a href=\"mailto:$sems_config->{postmaster}\">Mail Newtec</a></address>
  </body>
EOF
	return ({}, $read_error) ;
    }

    # read file into variable

    if ($stderr_logging)
    {
	print STDERR "Reading $filename\n";
    }

    my $data = do $filename;

#     print STDERR "for $filename, got data : \n", Dumper($data);

    my $read_error = undef;

    if ($@)
    {
	if ($stderr_logging)
	{
	    print STDERR "Error for $filename : $@\n";
	}

	my $sems_config = do $sems_config_file;

	my $read_error = <<EOF;
  <body>
    <h1>Error</h1>
    Error reading '$filename' : $@
    <hr>
    <address><a href=\"mailto:$sems_config->{postmaster}\">Mail Newtec</a></address>
  </body>
EOF
	return ({}, $read_error) ;
    }

    # check syntax

    $_ = file2str($filename);

    my $success = 1;

    my $unfound_key ;

    my $matcher;

    my $count = 0;

    foreach my $key (keys %{$config->{tags}})
    {
	my $tag = $config->{tags}->{$key};

	if (exists $tag->{required}
	    && ($tag->{required} eq 'yes'))
	{
	    $matcher = $tag->{keys}->[0] . "(.|\n)*" . $tag->{keys}->[1] ;

	    if (!/$matcher/m)
	    {
		$unfound_key = $key;

		$success = 0;

		last;
	    }
	}

	$count++;
    }

    # report syntax failure if necessary

    if ($success == 0)
    {
	if ($stderr_logging)
	{
	    print STDERR "Error for $filename : $@\n";
	}

	my $sems_config = do $sems_config_file;

	$read_error = <<EOF
  <body>
    <h1>Error</h1>
    Error parsing '$filename' : invalid syntax
    <p>count is $count, did not find section '$unfound_key'
    <hr>
    <address><a href=\"mailto:$sems_config->{postmaster}\">Mail Newtec</a></address>
  </body>
EOF

    }

    if ($stderr_logging)
    {
	print STDERR "Success for $filename\n";
    }

    # return read config and error message

    return ($data, $read_error) ;
}


# You must first check with any_config_read() to check if the config file is
# ok before calling this function.
#
# A session mechanism could solve this, i.e. in the context of the session a
# one-time check is made with any_config_read() to see if the config file is
# ok.

sub any_config_restore
{
    # result : false : didn't write anything
    #          true  : ok

    my $result = 1;

    # type of file

    my $type = shift;

    my $config = $all_configs->{$type};

    # sections to be restored

    my $keys = shift;

    my ($file, $read_error) = any_config_read($type);

    my $filename = $config->{filename};

    my $factory_config_str = file2str(get_factory_name($filename));

    my $new_config_str = file2str($filename);

    foreach my $key (@$keys)
    {
	if ($stderr_logging)
	{
	    print STDERR "Restoring ($type,$key)\n";
	}

	# extract restore string

	my $matcher
	    = ""
		. quotemeta($config->{tags}->{$key}->{keys}->[0])
		    . "((^#[^\n]*\n)*)"
			. "((.|\n)*)"
			    . quotemeta($config->{tags}->{$key}->{keys}->[1])
		  ;
	$factory_config_str =~ m/($matcher)/m;

	my $replacement = $1;

	$new_config_str =~ s/$matcher/$replacement/m;
    }

    $result = create_backup_and_write($filename, $new_config_str);

    return $result;

}


#
# set the owner of all the given config files.
#

sub any_config_set_owner
{
    #t should consult the info database to figure out the owners.

    my $user = shift;

    my @files = @_;

    # set owner of old and new file to 'sems'

    my ($login,$pass,$uid,$gid) = getpwnam($user);

    foreach (@files)
    {
	chown $uid, $gid, $_;

	chown $uid, $gid, $_;
    }
}


sub any_config_specification
{
    my $type = shift;

    my $config = $all_configs->{$type};

    # if the config specification does not exist yet

    if (!exists $config->{specification})
    {
	# if the config does not provide a specification name

	if (!exists $config->{specification_name})
	{
	    # no specification for this config

	    return undef;
	}

	my $specification_name = $config->{specification_name};

	# try to read the specification from the database

	require Sesa::Persistency::Specification;

	import Sesa::Persistency::Specification qw(specification_read);

	my ($config_specification, $read_error) = specification_read($specification_name);

	if (!$read_error)
	{
	    $config->{specification} = $config_specification;
	}
	else
	{
	    return undef;
	}
    }

    # return the specification

    my $specification = $config->{specification};

    return $specification;
}


#
# overwrite a config section with the data in $_[1].
#
# Note that the content data to be written must be a hash.
#
# returns : success of operation.
#

sub any_config_write
{
    # result : false : didn't write anything
    #          true  : ok

    my $result = 1;

    # type of file

    my $type = shift;

    my $config = $all_configs->{$type};

    # factory backup or config file ?

    my $selection = shift;

    # data to be written

    my $data = shift;

    # keys to extract from data and write to the config file

    my $keys = shift;

    # the sorter that sorts things for Data::Dumper.

    my $sorter =
	sub
	{
	    # sort hash keys in alphabetical order

	    my $hash = shift;

	    my $order = [
			 sort { uc($a) cmp uc($b) }
			 keys %$hash
			];

	    return $order;
	};

    # if config checker for this type

    if (exists $config->{is_valid}
        && $config->{is_valid})
    {
	my $sub = $config->{is_valid};

	my $is_valid = &$sub($type, $data, $keys);

	if (!$is_valid)
	{
	    if ($stderr_logging)
	    {
		print STDERR "any_config_write(): did not write anything, config data is not valid.\n";
	    }

	    return 0;
	}
    }

    # normally we will write to the regular config file

    my $filename = $config->{filename};

    # but the factory file can be selected too.

    if ($selection eq 'factory')
    {
	$filename = get_factory_name($filename);
    }

    my $old_file = file2str($filename);

    my $new_file;

    # get variable used

    my $varname = any_config_get_varname($filename);

    # loop over all replacement requests

    $new_file = $old_file;

    foreach my $key (@$keys)
    {
	# if the info for this key is not found

	if (!exists $config->{tags}->{$key}
	    || !exists $config->{tags}->{$key}->{keys}
	    || !exists $config->{tags}->{$key}->{keys}->[0]
	    || !exists $config->{tags}->{$key}->{keys}->[1])
	{
	    if ($stderr_logging)
	    {
		print STDERR "any_config_write(): did not write anything, tags not found (internal error).\n";
	    }

	    # return failure

	    return 0;
	}

	if ($stderr_logging)
	{
	    print STDERR "--------------\nWriting $key\n";
	}

	# keys in config file default to single key in spec array, ...

	my $config_keys = [ $key, ];

	# ... but can be overriden by spec array.

	if (exists $config->{tags}->{$key}->{config_keys})
	{
	    $config_keys = $config->{tags}->{$key}->{config_keys};
	}

	# produce a matcher string

	my $matcher
	  = ""
	    . quotemeta($config->{tags}->{$key}->{keys}->[0])
	      . "((^#[^\n]*\n)*)"
		. "((.|\n)*)"
		  . quotemeta($config->{tags}->{$key}->{keys}->[1])
		    ;

 	$old_file =~ m/$matcher/m ;

 	# produce replacement

	my $replacement = '';

	$replacement .= $config->{tags}->{$key}->{keys}->[0];
	$replacement .= $1 . "\n";

	# loop over all keys in the config file for this particular section.

	foreach my $config_key (@$config_keys)
	{
	    my $content;

	    my $config_key_replacement;

	    # if the config key puts the content in a structure

	    if ($config_key =~ /^[{[].*[]}]$/)
	    {
		# get data of interest using eval

		#! e.g. $config_key is '{a}->{b}'

		$content = eval "\$data->$config_key";

		$config_key_replacement = "$config_key";
	    }

	    # else

	    else
	    {
		# get data of interest directly

		$content = $data->{$config_key};

		$config_key_replacement = "{$config_key}";
	    }

	    if ($stderr_logging)
	    {
		print
		    STDERR
			"Content for $config_keys is $config_key\n",
			    Dumper($content),
				"\n";
	    }

	    # check type of data to write

	    local $_ = ref($content);

	TYPE:
	    {
		# for a hash

		/^HASH$/ and do
		{
		    # register all key entries of the hash

		    foreach my $entry (sort { uc($a) cmp uc($b) } keys %$content)
		    {
			if ($stderr_logging)
			{
			    print STDERR "Adding $entry\n";
			}

			$replacement .= '$' . $varname . "${config_key_replacement}->{'$entry'} =\n" ;
			$replacement
			    .= clean_dump('',
					  $content->{$entry},
					  sort => $sorter,
					 );
		    };
		    last TYPE;
		};

		# for an array

		/^ARRAY$/ and do
		{
		    # register full array once

		    $replacement .= '$' . $varname . "$config_key_replacement =\n" ;
		    $replacement
			.= clean_dump('',
				      $content,
				      sort => $sorter,
				     );
		    last TYPE;
		};

		# this must be a string : register it

		$replacement .= '$' . $varname . "$config_key_replacement =\n" ;
		$replacement .= clean_dump('', $content, );
	    }
	}

	# register terminator tag

	$replacement .= "\n" . $config->{tags}->{$key}->{keys}->[1];

	if ($stderr_logging)
	{
	    print STDERR "Replacement is \n-------------\n$replacement\n-------------\n";
	}

	# do the replacement

	$new_file =~ s/$matcher/$replacement/m;
    }

    # create backup and write

    $result = create_backup_and_write($filename, $new_file);

    return $result;
}


#
# create a sensible backup filename.
#
# $_[0] : fully qualified filename.
#

sub create_backup_name
{
    my $filename = shift ;

    my $count = 0;

    my $backup_name = "$filename~$count";

    # loop over backups to determine oldest backup

    my $oldest = $count;

    my $ctime_oldest = 9999999999; # 1118654454;

    while (-e $backup_name)
    {
	# get inode change time

	my ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime,
	    $mtime, $ctime, $blksize, $blocks)
	    = stat($backup_name);

	# keep track of oldest name.

	if ($ctime_oldest > $ctime)
	{
	    $ctime_oldest = $ctime;
	    $oldest = $count;
	}

	# check next backup name ...

	$count++;

	# ... but stop at wrap value

	if ($count > 20)
	{
	    # need to replace oldest file.

	    $count = $oldest;

	    # oldest file known, break loop

	    last;
	}

	# compute next backup name

	$backup_name = "$filename~$count";
    }

    # return possibly new backup name

    return("$filename~$count");
}


#
# create a backup and write new content.
#
# $_[0] : fully qualified filename.
#
# $_[1] : new content of file.
#

sub create_backup_and_write
{
    my $filename = shift;

    my $contents = shift;

    # compute a sensible backup name

    my $backup_name = create_backup_name($filename);

    # old file is now owned by root

    chown 0, 0, $filename;

    # move the old file

    rename $filename, $backup_name ;

    # write new content to new file

#     str2file($contents, $filename);

    use YAML 'DumpFile';

    eval
    {
	DumpFile($filename, $contents);
    };

#     # set owner of old and new file to 'sems'

#     any_config_set_owner('sems', $backup_name, $filename, );

    return 1;
}


#
# create a backup with factory settings.
#
# $_[0] : fully qualified filename.
#

sub create_factory_backup
{
    my $fullpath = shift;

    $fullpath =~ m|(.*)/(.*)|;

    my $factory_name = get_factory_name($fullpath);

    my $factory_master_name = get_factory_master_name($fullpath);

    if ( ! -e $factory_name)
    {
	# normally the factory backup is created during installation.
	# ( in /sems/site_defaults/ )

	my $content = file2str($fullpath) || '';

	str2file($content, $factory_name);

	str2file($content, $factory_master_name);

	if ($stderr_logging)
	{
	    print STDERR "Writing backup for $fullpath : $factory_name\n";
	}
    }
    else
    {
	if ($stderr_logging)
	{
	    print STDERR "Already created factory name $factory_name\n";
	}
    }
}


#
# Get filename of file with factory settings, given filename of file with
# actual settings.
#
# $_[0] : fully qualified filename.
#

sub get_factory_master_name
{

    my $fullpath = shift ;

    my $factory_name = $fullpath;

    #! I have the strong conviction that this line does not do anything at all...

    $factory_name =~ s(/var/sems/)(/sems/site_defaults/)s;

    return("$fullpath.factory.master");
#    return($factory_name);
}


sub get_factory_name
{

    my $fullpath = shift ;

    my $factory_name = $fullpath;

    #! I have the strong conviction that this line does not do anything at all...

    $factory_name =~ s(/var/sems/)(/sems/site_defaults/)s;

    return("$fullpath.factory");
#    return($factory_name);
}


1;


