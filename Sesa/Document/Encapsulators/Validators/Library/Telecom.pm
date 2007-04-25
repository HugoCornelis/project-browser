#!/usr/bin/perl -w
#!/usr/bin/perl -d:ptkdb -w
#!/usr/bin/perl -w
#
# $Id: Telecom.pm,v 1.2 2005/06/29 12:51:39 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be
#


package Sesa::Document::Encapsulators::Validators::Library::Telecom;


use strict;


use Sesa::Document::Encapsulators::Validators::Library::Standard;


sub _validate_rf_frequency
{
    my $self = shift;

    my $name = shift;

    my $label = shift;

    my $path = shift;

    my $rf_lower_limit = 1000000;

    my $rf_upper_limit = 50000000;

    #! note : form_path and $path must be the same string, form_path currently not used.

    my $java_script = "
function $name(form_name,sesa_path)
{
    var element = document.getElementById('$path');

    var value = element.value;

    var regex_number = /^[0-9.,]+\$/;

    if (!regex_number.test(value))
    {
	alert('Numeric entry expected for $label. ($path)');

	element.focus();

	element.select();

	return false;
    }

    if (value < $rf_lower_limit || $rf_upper_limit < value)
    {
	alert('$label ' + value + ' is not in range, expecting a value between $rf_lower_limit and $rf_upper_limit. ($path)');

	element.focus();

	element.select();

	return false;
    }

    return true;
}

";

    my $result
	= {
	   name => $name,
	   path => $path,
	   script => $java_script,
	   type => 'javascript',
	  };

    return $result;
}


Sesa::Document::Encapsulators::Validators::Library::Standard::configure(__PACKAGE__);


