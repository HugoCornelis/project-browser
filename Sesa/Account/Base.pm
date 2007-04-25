#!/usr/bin/perl -w
#
# $Id: Base.pm,v 1.3 2005/03/24 16:58:57 hco Exp $
#

#
# Sesa accounts live in the same space as Webmin accounts and groups.
#
# ->add() : add the account.
#
# ->remove() : remove the account.
#
# ->modify() : modify an existing account.
#

package Sesa::Account::Base;


use strict;


use NTC::FilePatch;


#
# acl_file_patches()
#
# Create a list of file patches for the acl list for the given
# account.  Since Webmin mixes the group and user name space, the
# account can be a user account as well as a group account.
#
#t this code is based on the code in the sesa target install script.
#t Should synchronize the code.
#t

sub acl_file_patches
{
    my $self = shift;

    # create a list of file patches

    my $result = [];

    # get name of the account

    my $account_name = $self->{name};

    # loop over all modules

    my $modules = $self->{modules};

    foreach my $module (keys %$modules)
    {
	# create file patch object with overall details

	my $action = 'create';

	my $filename;

	if ($module eq 'net'
	    || $module eq 'time')
	{
	    $filename = "webmin/${module}/${account_name}.acl";
	}
	else
	{
	    $filename = "webmin/sems_${module}/${account_name}.acl";
	}

	my $filepatch
	    = NTC::FilePatch->new
		(
		 $action,
		 $filename,
		);

	# create hunk header details

	my $hunk
	    = {
	       offset_orig => 0,
	       text => '',
	      };

	# loop over the submodules for this module

	my $submodules = $modules->{$module};

	foreach my $submodule (keys %$submodules)
	{
	    # add to hunk text : access for this account to this submodule

	    $hunk->{text} .= "+$submodule=$submodules->{$submodule}\n";
	}

	# add the hunk to the file patch object

	$filepatch->add_hunks({ hunks => [ $hunk, ], }, );

	# add file patch object to file patch list

	push @$result, $filepatch;
    }

    # return result

    return $result;
}


#
# add()
#
# Add this account to the Webmin accounts.
#

sub add
{
    die "->add() not implemented for $_[0]";
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

    if (!$self->{groups})
    {
	$self->{groups} = [];
    }

    if (!$self->{modules})
    {
	$self->{modules} = {};
    }

    if (!$self->{members})
    {
	$self->{members} = [];
    }

    bless ($self, $class);

    return $self;
}


#
# remove()
#
# Remove this account from the Webmin accounts.
#

sub remove
{
    die "->remove() not implemented for $_[0]";
}


#
# synchronize_with_groups()
#
# Synchronize the list of modules with the list of groups by adding
# the modules listed in the groups.
#

sub synchronize_with_groups
{
    my $self = shift;

    my $groups = `cat /etc/webmin/webmin.groups`;

    foreach my $group (@{$self->{groups}})
    {
	$groups =~ m/^$group:[^:]*:([^:]*):/;

	my $group_modules = $1;

	$group_modules = [ split ' ', $group_modules ];

	push @{$self->{modules}}, @$group_modules;
    }
}


1;


