#!/usr/bin/perl -w
#
# $Id: User.pm,v 1.3 2005/04/07 09:36:08 hco Exp $
#

package Sesa::Account::User;


#
# Abstraction of a Webmin user.  Basically allows to install and
# remove Webmin users.
#


use strict;


use base qw(Sesa::Account::Base);


#t For the moment this sub writes the info directly to Webmin's config
#t files.  It is therefore not possible to add the same group multiple
#t times without misconfiguring Webmin.

sub add
{
    my $self = shift;

    $self->synchronize_with_groups();

    my $text_line = "$self->{name}";

    $text_line .= ":";

    $text_line .= join ' ', map { "sems_$_" } keys %{$self->{modules}}, "\n";

    `echo >>/etc/webmin/webmin.acl -n "$text_line"`;

    $text_line = "$self->{name}:$self->{password}:0::\n";

    `echo >>/etc/webmin/miniserv.users -n "$text_line"`;

    `rm -f /etc/webmin/module.infos.cache`;
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

    my $acls = `cat /etc/webmin/webmin.acl`;

    $acls =~ s/^$self->{name}:.*\n//g;

    `echo >/etc/webmin/webmin.acl -n "$acls"`;

    my $users = `cat /etc/webmin/miniserv.users`;

    $users =~ s/^$self->{name}:.*\n//g;

    `echo >/etc/webmin/miniserv.users -n "$users"`;

    `rm 2>/dev/null -f /etc/webmin/module.infos.cache`;
}


1;


