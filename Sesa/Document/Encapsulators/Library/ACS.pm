#!/usr/bin/perl -w
#!/usr/bin/perl -d:ptkdb -w
#!/usr/bin/perl -w
#
# $Id: ACS.pm,v 1.3 2005/06/29 14:20:07 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be
#


package Sesa::Document::Encapsulators::Library::ACS;


use strict;


use Sesa::Document::Encapsulators::Library::Standard;


my $bands_database = do "/var/sems/acs/bands";

my $all_bands = [ keys %{$bands_database->{acs_bands}}, ];

my $channel_database = do "/var/sems/acs/channel_database";

my $all_channels = [ keys %{$channel_database->{acs_channels_definitions}}, ];

my $satellite_database = do "/var/sems/acs/satellites";

my $all_satellites = [ keys %{$satellite_database->{acs_satellites}}, ];

my $present_satellites = [ grep { $satellite_database->{acs_satellites}->{$_}->{present} } @$all_satellites, ];


sub _decapsulate_any_band
{
    my ($self, $path, $column, $contents, $value, $options) = @_;

    return($path, $value);
}


sub _decapsulate_any_channel
{
    my ($self, $path, $column, $contents, $value, $options) = @_;

    return($path, $value);
}


sub _decapsulate_present_satellite
{
    my ($self, $path, $column, $contents, $value, $options) = @_;

    return($path, $value);
}


sub _encapsulate_any_band
{
    my ($self, $path, $column_number, $content, $options) = @_;

    return
	$self->{CGI}->popup_menu
	    (
	     -default => $content,
	     -name => "field_$path",
	     -override => 1,
	     -values => [ "None selected", @$all_bands, ],
	    );
}


sub _encapsulate_any_channel
{
    my ($self, $path, $column_number, $content, $options) = @_;

    return
	$self->{CGI}->popup_menu
	    (
	     -default => $content,
	     -name => "field_$path",
	     -override => 1,
	     -values => [ "None selected", @$all_channels, ],
	    );
}


sub _encapsulate_present_satellite
{
    my ($self, $path, $column_number, $content, $options) = @_;

    return
	$self->{CGI}->popup_menu
	    (
	     -default => $content,
	     -name => "field_$path",
	     -override => 1,
	     -values => [ "None selected", @$present_satellites, ],
	    );
}


Sesa::Document::Encapsulators::Library::Standard::configure(__PACKAGE__);


