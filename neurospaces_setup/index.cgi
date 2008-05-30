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
#     $ENV{WEBMIN_CONFIG} = 'usermin';

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
		  neurospaces_setup => {
					level => (our $editable = 1 && \$editable),
					label => 'setup project-browser session',
				       },
		 );
# use Sesa::Persistency::Specification qw(
# 					specification_get_icon
# 					specification_get_module_directory
# 					specification_read
# 					specification_write
# 				       );
# use Sesa::TableDocument;
# use Sesa::Transform;
# use Sesa::TreeDocument;
# use Sesa::Workflow;


my $query = CGI->new();


use YAML 'LoadFile';

my $neurospaces_config = LoadFile('/etc/neurospaces/project_browser/project_browser.yml');

my $project_root = $neurospaces_config->{project_browser}->{root_directory};

my $project_name = $query->param('project_name');

my $subproject_name = 'setup';

my $component_name = $query->param('component_name');

my $operation_name = $query->param('operation_name');

my $picture_name = $component_name; # $query->param('picture_name');


sub main
{
#     if (!-r $project_root)
    {
	&header('Project Browser Session Setup', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	system "cd /tmp && export DISPLAY=$ENV{REMOTE_ADDR}:0.0 && nohup sudo -H -u $ENV{REMOTE_USER} xhost + &";

	use Data::Dumper;

	if ($? == 0)
	{
	    print "Session setup succesful\n";
	}
	else
	{
	    print "Session setup unsuccesful\n";
	}

	print "<verbatim>\n";

	print "<code>\n";

	print Dumper(\%ENV);

	print "</code>\n";

	print "</verbatim>\n";

	print "<h3>Done.</h3>";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
}


main();


