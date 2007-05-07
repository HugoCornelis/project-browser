#!/usr/bin/perl -w
#!/usr/bin/perl -d:ptkdb -w
#
# (C) 2007 Hugo Cornelis hugo.cornelis@gmail.com
#


use strict;


use CGI;

use Data::Dumper;


BEGIN
{
    require '../web-lib.pl';

    #! for Sesa related modules

    push @INC, "..";

    #! for neurospaces and ssp related modules

    push @INC, "/usr/local/glue/swig/perl";

}


our $editable;


use Sesa::Sems qw(
		  documents_formalize
		  documents_merge_data
		  documents_parse_input
		 );

use Sesa::Access (
		  neurospaces_readcell2ndf => {
					       level => (our $editable = 1 && \$editable),
					       label => 'ssp schedules and their output',
					      },
		 );
# use Sesa::Persistency::Specification qw(
# 					specification_get_icon
# 					specification_get_module_directory
# 					specification_read
# 					specification_write
# 				       );
use Sesa::TableDocument;
use Sesa::Transform;
use Sesa::TreeDocument;
use Sesa::Workflow;


my $query = CGI->new();


my $neurospaces_config = do '/var/neurospaces/neurospaces.config';


sub document_readcell2ndf_configuration
{
    my $header = "readcell2ndf configuration";

    my $document_schedules
	= Sesa::TreeDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     contents => $neurospaces_config->{readcell2ndf},
	     header => $header,
	     name => 'readcell2ndf',
	     output_mode => 'html',
 	     sort => sub { return $_[0] cmp $_[1]; },
	    );

    return [ $document_schedules, ];
}


sub formalize_readcell2ndf_configuration
{
    my $documents = shift;

    documents_formalize($documents, { rulers => 1, }, );
}


sub main
{
    if (!$neurospaces_config
	|| !$neurospaces_config->{readcell2ndf})
    {
	&header('readcell2ndf configuration', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<H3>The configuration cannot be found in '/var/neurospaces/neurospaces.config'.</H3>";

	print "<p>\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
    else
    {
	&header("readcell2ndf configuration", "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	my $documents = document_readcell2ndf_configuration();

	my $data = documents_parse_input($documents);

	documents_merge_data($documents, $data);

	formalize_readcell2ndf_configuration($documents);

	# finalize (web|user)min specific stuff.

	&footer("/?cat=neurospaces", 'Neurospaces index');
    }
}


main();


