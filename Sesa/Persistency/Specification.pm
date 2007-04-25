#!/usr/bin/perl -w
#!/usr/bin/perl -d:ptkdb -w
#!/usr/bin/perl -w
#
# $Id: Specification.pm,v 1.10 2005/08/03 09:35:58 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be

package Sesa::Persistency::Specification;


use strict;


use Sesa::Persistency qw(
			 any_config_create
			 any_config_properties
			 any_config_read
			 any_config_restore
			 any_config_write
			 persistency_info_add
			 persistency_info_exists
			);


require Exporter;


our @ISA = qw(Exporter);

our @EXPORT_OK = qw(
		    specification_get_icon
		    specification_get_module_directory
		    specification_read
		    specification_write
		   );


my $specification_database_directory = '/sems/sesa/persistency/database/';


# tags that delimit the individual sections in the config file.

my $specification_tags
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
       'version-info' => {
			  'config_keys' => [
					    'version_info',
					   ],
			  'keys' => [
				     "## -!- Sems section : version-info -!-\n",
				     "## -!- Sems section : end version-info -!-\n",
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
       'column-specification' => {
				  'config_keys' => [ 'column_specification', ],
				  'keys' => [
					     "## -!- Sems section : column-specification -!-\n",
					     "## -!- Sems section : end column-specification -!-\n"
					    ],
				  'required' => 'no',
				  'shared' => 'global',
				 },
       'header-labeling' => {
			     'config_keys' => [ 'header_labeling', ],
			     'keys' => [
					"## -!- Sems section : header-labeling -!-\n",
					"## -!- Sems section : end header-labeling -!-\n"
				       ],
			     'required' => 'no',
			     'shared' => 'global',
			    },
      };

# specification info table

#! this table is a template only, it is never used.

my $specification_database_info
    = {
       'name' => 'specification',
       'filename' => $specification_database_directory,
#        'is_valid'
#        => sub { return(exists $_[1]->{acs_channels_definitions_version} && $_[1]->{acs_channels_definitions_version} == 1); },
       'tags' => $specification_tags,
      };


#
# specification_register()
#
# Register a specification file.  A specification file specifies the
# label, unit and order of a table to be rendered with
# Sesa::TableDocument.  The default specification is given with the
# key 'column-specification'.  If the key 'column-specifications'
# exists, it is used to override this default.  This allows to specify
# multiple tables in one specification file, i.e. define submodules.
# Each submodule comes in a seperate section in the config file.  The
# tags that define these sections should be given with the key 'tags'.
#

sub specification_register
{
    my $name = shift;

    my $specification_name = "specification_$name";

    # if this specification does not exist yet

    if (!persistency_info_exists($specification_name))
    {
	# create a specification for this name

	my $specification_name_database_info
	    = {
	       'name' => $specification_name,
	       'filename' => $specification_database_directory . $name,
	       'tags' => { %$specification_tags, },
	      };

	# register this specification to make it accessible for the persistency layer

	my $result = persistency_info_add($specification_name, $specification_name_database_info);

	# read the specification file

	my ($specification, $read_error) = any_config_read($specification_name);

	if ($read_error)
	{
	    return 0;
	}

	# if this one contains a tags section

	if (exists $specification->{persistency_tags})
	{
	    # delete the 'column-specification' key

	    delete $specification_name_database_info->{tags}->{'column-specification'};

	    # add the tags given in the specification file

	    #! note : in place operation in already registered persistency info

	    #! note : checking if required sections are present is not possible this way

	    my $inherited_tags = $specification_name_database_info->{tags};

	    my $persistency_tags = $specification->{persistency_tags};

	    $specification_name_database_info->{tags}
		= {
		   %$inherited_tags,
		   %$persistency_tags,
		  };
	}

	# return success of operation

	return $result;
    }

    # specification already existed

    else
    {
	#t should compare : use NTC::Data::Comparator of the Sesa test framework.

	# for the moment this is ok, return success

	return 1;
    }
}


# not ready for export yet

sub specification_create
{
    my $name = shift;

    if (!specification_register($name))
    {
	return 0;
    }

    # create the config

    my $specification_name = "specification_$name";

    return any_config_create($specification_name, @_);
}


# not ready for export yet

sub specification_exists
{
    my $name = shift;

    if (!specification_register($name))
    {
	return undef;
    }

    my $specification_name = "specification_$name";

    my $properties = any_config_properties($specification_name, @_);

    return($properties->{exists});
}


sub specification_get_icon
{
    my $args = shift;

    # return information from the inventory, default : label editor icon (this is currently hardcoded)

    my $result = specification_get_module_directory($args, @_);

    my $file_prefix = "/usr/libexec/webmin/";

    my $filename = $file_prefix . $result . "/images/icon.gif";

    #t hardcoded construct, relates to the install location of webmin,
    #t and the fact if we are running over apache or stand-alone.

#     my $http_prefix = "/webmin/";

    my $http_prefix = "/";

    if (-r $filename)
    {
	$result = $http_prefix . $result . "images/icon.gif";
    }
    else
    {
	$result = $http_prefix . "sems_sesa_persistency_editor/" . "images/labels.gif";
    }

    return $result;
}


sub specification_get_module_directory
{
    my $args = shift;

    # return information from the inventory, default : label editor icon (this is currently hardcoded)

    my $result;

    my $icon_specification = $args->{icon_specification};

    my $modules = $args->{module};

    my $specification_name = $modules->[0];

    my ($specification, $read_error) = specification_read($specification_name, );

    $result = $specification->{inventory_info}->{module_directory};

    return $result;
}


sub specification_read
{
    my $name = shift;

    if (!specification_register($name))
    {
	return ({}, "Could not register the specification in the persisency layer (internal error)");
    }

    # create the config

    my $specification_name = "specification_$name";

    return any_config_read($specification_name, @_);
}


# You must first check with specification_read() for the same
# specification file to check if the config file is ok before calling
# this function.

sub specification_restore
{
    my $name = shift;

    if (!specification_register($name))
    {
	return 0;
    }

    # create the config

    my $specification_name = "specification_$name";

    return any_config_restore($specification_name, @_);
}


sub specification_write
{
    my $name = shift;

    if (!specification_register($name))
    {
	return 0;
    }

    # create the config

    my $specification_name = "specification_$name";

    return any_config_write($specification_name, 'config', @_);
}


1;


