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
		  neurospaces_project_browser => {
						  level => (our $editable = 1 && \$editable),
						  label => 'projects, project modes and project modules',
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

my $project_name = $query->param('project_name');

my $mode_name = $query->param('mode_name') || 'modules';

my $module_name = $query->param('module_name');


sub formalize_project
{
    my $project_name = shift;

    my $mode_name = shift;

    my $project_root = $neurospaces_config->{simulation_browser}->{root_directory};

    # get all information from the database

    my $all_modules = [ sort map { chomp; $_; } `/bin/ls -1 "$project_root/$project_name/$mode_name"`, ];

    my @links;
    my @titles;
    my @icons;

    foreach my $module_name (@$all_modules)
    {
	#    if ($access{$subschedule})
	{
	    push(@links, "?project_name=${project_name}&mode_name=${mode_name}&module_name=${module_name}");
	    push(@titles, $module_name);

	    my $icon = 'images/icon.gif';

	    push(@icons, $icon, );
	}
    }

    &icons_table(\@links, \@titles, \@icons);

    print "<hr>" ;

}


sub formalize_project_root
{
    my $project_root = $neurospaces_config->{simulation_browser}->{root_directory};

    # get all information from the database

    my $all_projects = [ sort map { chomp; $_; } `/bin/ls -1 "$project_root"`, ];

    my @links;
    my @titles;
    my @icons;

    foreach my $project_name (@$all_projects)
    {
	#    if ($access{$subschedule})
	{
	    push(@links, "?project_name=${project_name}");
	    push(@titles, $project_name);

	    my $icon = 'images/icon.gif';

	    push(@icons, $icon, );
	}
    }

    &icons_table(\@links, \@titles, \@icons);

    print "<hr>" ;

}


sub main
{
    if (!-r $neurospaces_config->{simulation_browser}->{root_directory})
    {
	&header('Project Browser and Editor', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<H3>The projects directory does not exist.</H3>";

	print "<p>\n";

	print "$neurospaces_config->{simulation_browser}->{root_directory} not found\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
    elsif (!$mode_name)
    {
	&header('Project Browser and Editor', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<H3>The mode_name is not defined.</H3>";

	print "<p>\n";

	print "This is an internal error\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
    elsif (!$project_name)
    {
	&header("Project Browser", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_project_root();

	# finalize (web|user)min specific stuff.

	&footer("index.cgi", 'Project Browser');
    }
    elsif (!$module_name)
    {
	&header("Project Browser: $project_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_project($project_name, $mode_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi", 'Project Browser');
    }
    else
    {
	my $url = "/neurospaces_output_browser/?";

	my $args = [];

	foreach my $argument_name (
				   qw(
				      project_name
				      mode_name
				      module_name
				     )
				  )
	{
	    my $value = eval "\$$argument_name";

	    if ($value)
	    {
		push @$args, "$argument_name=$value";
	    }
	}

	$url .= join '&', @$args;

	&redirect($url, 'Output Browser');
    }
}


main();


