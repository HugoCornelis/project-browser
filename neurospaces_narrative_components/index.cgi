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
		  neurospaces_narrative_components => {
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


use YAML 'LoadFile';

my $neurospaces_config = LoadFile('/etc/neurospaces/project_browser/project_browser.yml');

my $project_root = $neurospaces_config->{project_browser}->{root_directory};

my $project_name = $query->param('project_name');

my $subproject_name = 'narrative_components';

my $component_name = $query->param('component_name');

my $operation_name = $query->param('operation_name');

my $picture_name = $component_name; # $query->param('picture_name');


sub formalize_components
{
    my $project_name = shift;

    # load module specifics

    use YAML 'LoadFile';

    my $module_description;

    my $module_configuration;

    eval
    {
	$module_configuration = LoadFile("$project_root/$project_name/$subproject_name/configuration.yml");
    };

    my $header = $module_configuration->{description} || 'Narrative Components';

    print STDERR "header is $header\n";

    print "<center><h3>$header</h3></center>\n";

    print "<hr>" ;

    # get all pictures specific to this module

    {
	print "<center><h4>Specific Components</h4></center>\n";

	my @links;
	my @titles;
	my @icons;

	my $module_pictures = $module_configuration->{pictures} || [];

	foreach my $picture (@$module_pictures)
	{
	    my $component_name = $picture->{name};
	    my $component_description = $picture->{description};

	    #    if ($access{$picture})
	    {
		push(@links, "?project_name=${project_name}&subproject_name=${subproject_name}&component_name=$component_name");
		push(@titles, $component_description);

		my $icon = 'images/icon.gif';

		push(@icons, $icon, );
	    }
	}

	&icons_table(\@links, \@titles, \@icons);

	print "<hr>" ;
    }

    print "<hr>" ;

}


sub formalize_component
{
    my $project_name = shift;

    my $component_name = shift;

    # load module specifics

    use YAML 'LoadFile';

    my $module_description;

    my $module_configuration;

    eval
    {
	$module_configuration = LoadFile("$project_root/$project_name/$subproject_name/configuration.yml");
    };

    my $header = $module_configuration->{description} || 'Narrative Components';

    print STDERR "header is $header\n";

    print "<center><h3>$header</h3></center>\n";

    print "<hr>" ;

    # check if a module picture was called

    print STDERR "checking for picture name\n";

    if ($component_name)
    {
	print STDERR "checking for picture name, found $picture_name\n";

	# first map the pictures to a hash

	my $module_pictures = $module_configuration->{pictures} || [];

	my $pictures
	    = {
	       map
	       {
		   ( $_->{name} => $_->{picture} );
	       }
	       @$module_pictures,
	      };

	my $picture_descriptions
	    = {
	       map
	       {
		   ( $_->{name} => $_->{description} );
	       }
	       @$module_pictures,
	      };

	print STDERR "module_pictures is:\n" . Dumper($pictures);

	# get picture to show

	my $picture = $pictures->{$component_name};

	$picture =~ s/\$project_root/$project_root/g;
	$picture =~ s/\$project_name/$project_name/g;

	$picture =~ s(//)(/)g;

	print "<center><h3>$picture_descriptions->{$component_name}</h3></center>\n";

	print "<img src=\"$picture\" alt=\"$picture\" border=\"0\" width=\"900\">";
    }
    else
    {
	print "<center><h3>Error: this component type is not yet implemented</h3></center>\n";

    }

    print "<hr>" ;

}


sub formalize_operation
{
    my $project_name = shift;

    my $component_name = shift;

    my $operation_name = shift;

#     my $command = $all_operations->{$operation_name}->{command};

#     print "<code>\n";

#     print "Executing:\n$command\n";

#     print "</code>\n";

#     print "<pre>\n";

#     my $output = `$command`;

#     my $count = ($output =~ tr/\n/\n/);

#     print "$count lines of output\n";

#     print $output;

#     print "</pre>\n";

    print "<hr>" ;

}


sub main
{
    if (!-r $project_root)
    {
	&header('Component Browser', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<h3>The projects directory does not exist.</h3>";

	print "<p>\n";

	print "$project_root not found\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
    elsif (!$project_name)
    {
	my $url = "/neurospaces_project_browser/";

	&redirect($url, 'Project Browser');
    }
    elsif (!$component_name)
    {
	&header("Component Browser: $project_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_components($project_name);

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'}, "/neurospaces_project_browser/?project_name=${project_name}", 'This Project', "/neurospaces_project_browser/", 'All Projects');
    }
    elsif (!$operation_name)
    {
	&header("Component Browser: $component_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_component($project_name, $component_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi?project_name=${project_name}", "Narrative Components");
    }
    else
    {
	&header("Component Browser: $component_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_operation($project_name, $component_name, $operation_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi?project_name=${project_name}", "Narrative Components");
    }
}


main();


