#!/usr/bin/perl -w
#
# $Id: Base.pm,v 1.1 2005/03/24 16:58:57 hco Exp $
#

package Sesa::Module::Base;


#
# Abstraction of a Webmin/Sesa module.  For Webmin only modules the
# functionality of this package is quite limited at the moment of
# writing.
#


use strict;


my $webmin_directory = "/usr/libexec/webmin";


#
# get_name()
#
# Returns the Sesa name of the module.
#

sub get_name
{
    my $self = shift;

    return $self->{name};
}


#
# get_submodules()
#
# Returns the in memory list of names of submodules.  Perhaps you
# might to synchronize first using ->read_submodules().
#

sub get_submodules
{
    my $self = shift;

    return $self->{submodules};
}


#
# get_webmin_name()
#
# Returns the Webmin name of the module.
#

sub get_webmin_name
{
    my $self = shift;

    my $name = $self->get_name();

    return "sems_$name";
}


sub new
{
    my $proto = shift;
    my $class = ref($proto) || $proto;
    my $options = shift;
    my $self = {};

    foreach my $key (keys %$options)
    {
	$self->{$key} = $options->{$key};
    }

    if (!$self->{submodules})
    {
	$self->{submodules} = {};
    }

    # name must exist

    if (!$self->{name})
    {
	return undef;
    }

    bless ($self, $class);

    return $self;
}


#
# read_submodules()
#
# Read the list of submodules from the module specification and add
# them to the (in memory) submodule list for this module.  This
# effectively overwrites already (in memory) submodules known by the
# same name.
#
# Returns success of operation
#
# This sub will only work for Sesa related modules.
#

sub read_submodules
{
    my $self = shift;

    my $name = $self->get_name();

    my $module_directory = "$webmin_directory/sems_$name";

    my $submodules_specifier = "$module_directory/submodules.pl";

    my $submodules = { 'noconfig' => 1, $name => 1, };

    if (-r $submodules_specifier)
    {
	my $real_submodules = do $submodules_specifier;

	$submodules = { %$submodules, %$real_submodules, };
    }

    $self->{submodules}
	= {
	   %{$self->{submodules}},
	   %$submodules,
	  };

    return 1;
}


1;


