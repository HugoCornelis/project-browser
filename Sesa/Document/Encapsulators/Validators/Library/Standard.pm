#!/usr/bin/perl -w
#!/usr/bin/perl -d:ptkdb -w
#!/usr/bin/perl -w
#
# $Id: Standard.pm,v 1.5 2005/07/19 11:43:49 hco Exp $
#
# (C) 2003-2005 Newtec Cy N.V. Laarstraat 5, B-9100 Sint-Niklaas, Belgium
# "http://www.newtec.be/"  support@newtec.be
#


package Sesa::Document::Encapsulators::Validators::Library::Standard;


use strict;


sub _validate_mandatory_textfield
{
    my $self = shift;

    my $name = shift;

    my $label = shift;

    my $path = shift;

    #! note : form_path and $path must be the same string, form_path currently not used.

    my $java_script = "
function $name(form_name,sesa_path)
{
    var element = document.getElementById('$path');

    var value = element.value;

    if (value == '')
    {
	alert('Element $label is mandatory. ($path)');

	element.focus();

	element.select();

	return false;
    }
    else
    {
	return true;
    }
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


sub _validate_number
{
    my $self = shift;

    my $name = shift;

    my $label = shift;

    my $path = shift;

    #! note : form_path and $path must be the same string, form_path currently not used.

    my $java_script = "
function $name(form_name,sesa_path)
{
    var element = document.getElementById('$path');

    var regex_number = /^-?[0-9.,]+\$/;

    if (!regex_number.test(element.value))
    {
	alert('Numeric entry expected for $label. ($path)');

	element.focus();

	element.select();

	return false;
    }
    else
    {
	return true;
    }
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


sub configure
{
    my $result = 1;

    no strict "refs";

    my $package = shift;

    foreach my $sub (keys %{"${package}::"})
    {
	if ($sub =~ /^(_validate_)/)
	{
	    my $exported_sub = $sub;

	    $exported_sub =~ s/^(_validate_)//;

	    no strict "refs";

	    *{"Sesa::Document::Encapsulators::Validators::$exported_sub"} = \&{"${package}::$sub"};
	}
    }

    return $result;
}


configure(__PACKAGE__);


