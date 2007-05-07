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
		  neurospaces_morphology_browser => {
						     level => (our $editable = 1 && \$editable),
						     label => 'projects, subprojects and project modules',
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

my $morphology_name = $query->param('morphology_name');


sub formalize_morphologies
{
    my $project_name = shift;

    my $project_root = $neurospaces_config->{simulation_browser}->{root_directory};

    # get all information from the database

    my $all_morphologies = [ sort map { chomp; $_; } `find "$project_root/$project_name/morphologies" -name "*.ndf" -o -name "*.p"`, ];

    my @links;
    my @titles;
    my @icons;

    foreach my $morphology_name (@$all_morphologies)
    {
	$morphology_name =~ s(^$project_root/$project_name/morphologies)();

	use YAML 'LoadFile';

	my $morphology_description;

	my $module_configuration;

	eval
	{
	    $module_configuration = LoadFile("$project_root/$project_name/morphologies/$morphology_name/configuration.yml");
	};

	$morphology_description = $module_configuration->{description} || $morphology_name;

	push(@links, "?project_name=${project_name}&morphology_name=${morphology_name}");
	push(@titles, $morphology_description);

	my $icon = 'images/icon.gif';

	if ($morphology_name =~ /.p$/)
	{
	    $icon = 'images/genesis.gif';
	}
	elsif ($morphology_name =~ /.ndf$/)
	{
	    $icon = 'images/ndf.gif';
	}

	push(@icons, $icon, );
    }

    &icons_table(\@links, \@titles, \@icons);

    print "<hr>" ;

}


sub formalize_morphology
{
    my $project_name = shift;

    my $morphology_name = shift;

    my $project_root = $neurospaces_config->{simulation_browser}->{root_directory};

    # get all information from the database

    my $all_subprojects = [ sort map { chomp; $_; } `/bin/ls -1 "$project_root/$project_name"`, ];

    my @links;
    my @titles;
    my @icons;

    my $known_subprojects;

    use YAML 'LoadFile';

    eval
    {
	$known_subprojects = LoadFile("$project_root/$project_name/configuration.yml");
    };

    foreach my $subproject_name (grep { $known_subprojects->{$_} } @$all_subprojects)
    {
	#    if ($access{$subschedule})
	{
	    my $link_target = $known_subprojects->{$subproject_name}->{link_target} || $subproject_name;

	    my $link = "?project_name=${project_name}&subproject_name=${link_target}";

	    push(@links, $link);
	    push(@titles, $known_subprojects->{$subproject_name}->{description} || $subproject_name);

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
	&header('Morphology Browser', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<h3>The projects directory does not exist.</h3>";

	print "<p>\n";

	print "$neurospaces_config->{simulation_browser}->{root_directory} not found\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
    elsif (!$project_name)
    {
	&header('Morphology Browser', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<h3>No Project Name defined, please return to the project browser.</h3>";

	print "<p>\n";

	print "$neurospaces_config->{simulation_browser}->{root_directory} not found\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'}, "/neurospaces_project_browser/", 'All Projects');
    }
    elsif (!$morphology_name)
    {
	&header("Morphology Browser: $project_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_morphologies($project_name);

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'}, "/neurospaces_project_browser/?project_name=${project_name}", 'This Project', "/neurospaces_project_browser/", 'All Projects');
    }
    else
    {
	&header("Morphology Browser: $morphology_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_morphology($project_name, $morphology_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi?project_name=${project_name}", "All Morphologies");
    }
}


main();


