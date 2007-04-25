#!/usr/bin/perl -w
#
# $Id: Group.pm,v 1.2 2005/03/24 16:58:57 hco Exp $
#

package Sesa::Account::Group;


#
# Abstraction of a Webmin group.  Basically allows to install and
# remove Webmin groups.
#


use strict;


use base qw(Sesa::Account::Base);


use NTC::Patch;


#t For the moment this sub writes the info directly to Webmin's config
#t files.  It is therefore not possible to add the same group multiple
#t times without misconfiguring Webmin.

sub add
{
    my $self = shift;

    my $text_line = "$self->{name}";

    $text_line .= ":";

    $text_line .= join ' ', @{$self->{members}};

    $text_line .= ":";

    #! converts sesa module names to webmin module names : add 'sems_' prefix

    $text_line .= join ' ', map { "sems_$_" } keys %{$self->{modules}};

    $text_line .= ":";

    $text_line .= ":";

    $text_line .= "\n";

    # install the group in the webmin configuration file

    `echo >>/etc/webmin/webmin.groups -n "$text_line"`;

    # create the list of file patches for the group acls

    my $acl_file_patches = $self->acl_file_patches();

    # install permissions for this particular group

    my $module_acl_patch
	= NTC::Patch->new
	    (
	     {
	      directory => '/etc/webmin/',
	      forward_options => [ '-p1', ],
	      function => "sesa_acls_for_group_$self->{name}",
	      file_patches => $acl_file_patches,
	     },
	    );

    # apply the patches (auto-generates the uninstall scripts for this particular function)

    $module_acl_patch->forward();

    # remove the webmin module info cache

    `rm 2>/dev/null -f /etc/webmin/module.infos.cache`;
}


sub new
{
    my $proto = shift;
    my $class = ref($proto) || $proto;

    my $self = $class->SUPER::new(
				  @_,
				 );

    # $self is ready for use

    bless ($self, $class);

    return $self;
}


sub remove
{
    my $self = shift;

    # remove the group from the webmin configuration

    my $groups = `cat /etc/webmin/webmin.groups`;

    $groups =~ s/^$self->{name}:.*\n//g;

    `echo >/etc/webmin/webmin.groups -n "$groups"`;

    # create the list of file patches for the group acls

    my $acl_file_patches = $self->acl_file_patches();

    # install permissions for this particular group

    my $module_acl_patch
	= NTC::Patch->new
	    (
	     {
	      directory => '/etc/webmin/',
	      forward_options => [ '-p1', ],
	      function => "sesa_acls_for_group_$self->{name}",
	      file_patches => $acl_file_patches,
	     },
	    );

    # remove the patches (normally uses the uninstall script)

    $module_acl_patch->reverse();

    # remove the webmin module info cache

    `rm 2>/dev/null -f /etc/webmin/module.infos.cache`;
}


1;


