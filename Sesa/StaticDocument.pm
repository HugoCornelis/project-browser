#!/usr/bin/perl -w
# $Id: StaticDocument.pm,v 1.4 2005/06/03 15:43:23 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be


package Sesa::StaticDocument;


use strict;

use CGI;

use Data::Dumper;

use Sesa::Document;


our @ISA = ("Sesa::Document");


sub new
{
    my $proto = shift;
    my $class = ref($proto) || $proto;
    my %options = @_;
    my $self = {};

    foreach my $key (keys %options)
    {
	$self->{$key} = $options{$key};
    }

    if ($self->{name} =~ /_/)
    {
	print STDERR "Document Error: Document names must not contain an '_'\n";

	my (
	    $package,
	    $filename,
	    $line,
	    $subroutine,
	    $hasargs,
	    $wantarray,
	    $evaltext,
	    $is_require,
	    $hints,
	    $bitmask
	   )
	    = caller(0);

	print STDERR "Document Error: at $filename:$line, $subroutine\n";

	require Carp;

	Carp::cluck "Document Error: at $filename:$line, $subroutine\n";
    }

    bless ($self, $class);

    $self->set_is_empty();

#     print STDERR Data::Dumper::Dumper($self);

    return $self;
}


# a static document has an static writer : it buffers everything till flushed.

sub writer
{
    my $self = shift;

    my $content = shift;

    if (!exists $self->{writer_output})
    {
	$self->{writer_output} = '';
    }

    $self->{writer_output} .= $content;

}


# print the generated result to STDOUT.

sub flush
{
    my $self = shift;

    print $self->{writer_output};
}


# remove the generated result.

sub unflush
{
    my $self = shift;

    $self->{writer_output} = '';
}


1;


## ======================================================================
## Local Variables:
## mode:               Cperl
## cperl-indent-level: 4
## mode:               auto-fill
## comment-column:     40
## fill-column:        78
## End:
