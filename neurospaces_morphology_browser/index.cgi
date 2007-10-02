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


use YAML 'LoadFile';

my $neurospaces_config = LoadFile('/etc/neurospaces/project_browser/project_browser.yml');

my $project_root = $neurospaces_config->{project_browser}->{root_directory};

my $project_name = $query->param('project_name');

my $morphology_name = $query->param('morphology_name');

my $morphology_name_short = $morphology_name;

if (defined $morphology_name_short)
{
    $morphology_name_short =~ s/.*\///;

    $morphology_name_short =~ s((.*)\..*$)(/$1);
}

my $operation_name = $query->param('operation_name');


my $all_operations;

if ($project_name && $morphology_name)
{
    #t the channel names should be coming from a library of from a project local configuration file.

    my $channel_names
	= {
	   cap => 'P type Calcium',
	   cat => 'T type Calcium',
	   h => 'Anomalous Rectifier',
	   k2 => 'Small Ca Dependent Potassium',
	   kC => 'Large Ca Dependent Potassium',
	   kdr => 'Delayed Rectifier',
	   km => 'Muscarinic Potassium',
	   naf => 'Fast Sodium',
	   nap => 'Persistent Sodium',
	  };

    $all_operations
	= {
	   (
	    map
	    {
		$_ => {
		       command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal-symbol / --reporting-field GMAX --condition '\$d->{context} =~ /$_/i' 2>&1",
		       description => "$channel_names->{$_} Densities",
		      };
	    }
	    keys %$channel_names,
	   ),
	   synchans => {
			command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal-symbol / --condition '\$d->{context} =~ m(par/exp)i' 2>&1",
			description => "Excitatory Synaptic Channels",
		       },
	   lengths => {
		       command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library  --traversal-symbol / --reporting-field LENGTH --type segment 2>&1",
		       description => "Compartment Lengths",
		      },
	   dias => {
		    command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library  --traversal-symbol / --reporting-field DIA --type segment 2>&1",
		    description => "Compartment Diameters",
		   },
	   lengths_cumulated => {
				 command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal-symbol / --reporting-field LENGTH --type '^T_sym_segment\$' --condition '\$d->{context} !~ /_spine/i' --operator cumulate 2>&1",
				 description => "Cumulated Compartment Length (no spines)",
				},
	   lengths_spiny_cumulated => {
				       command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal / --type '^T_sym_segment\$' --condition '\$d->{context} !~ /_spine/i && SwiggableNeurospaces::symbol_parameter_resolve_value(\$d->{_symbol}, \"DIA\", \$d->{_context}) < 3.18e-6' --reporting-field LENGTH --operator cumulate 2>&1",
				       description => "Cumulated spiny compartment lengths",
				      },
	   somatopetals => {
			    command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal-symbol / --reporting-field SOMATOPETAL_DISTANCE --type segment 2>&1",
			    description => "Somatopetal Lengths",
			   },
	   surface_spiny_cumulated => {
				       command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal / --type '^T_sym_segment\$' --condition '\$d->{context} !~ /_spine/i && SwiggableNeurospaces::symbol_parameter_resolve_value(\$d->{_symbol}, \"DIA\", \$d->{_context}) < 3.18e-6' --reporting-field SURFACE --operator cumulate 2>&1",
				       description => "Cumulated spiny compartment surface",
				      },
	   spines => {
		      command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --algorithm Spines 2>&1",
		      description => "Spines instance algorithm",
		     },
	   tips => {
		    command => "echo 'segmentertips $morphology_name_short' | neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --query 2>&1",
		    description => "Dendritic tips",
		   },
	   totalsurface => {
			    command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal / --type '^T_sym_cell\$' --reporting-field TOTALSURFACE 2>&1",
			    description => "Total dendritic surface",
			   },
	   totalsurface2 => {
			     command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal / --type '^T_sym_segment\$' --reporting-field SURFACE --operator cumulate 2>&1",
			     description => "Total dendritic surface (2)",
			    },
	  };

    # get project local information

    #t should be in a subdirectory and depend on the cgi $query params ?

    use YAML 'LoadFile';

    eval
    {
	$all_operations ||= LoadFile("$project_root/$project_name/morphologies/configuration.yml");
    };

}


sub formalize_morphologies
{
    my $project_name = shift;

    # get all information from the database

    my $all_morphologies = [ sort map { chomp; $_; } `find "$project_root/$project_name/morphologies" -name "*.ndf" -o -name "*.p" -o -iname "*.swc"`, ];

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

    my @links;
    my @titles;
    my @icons;

    foreach my $operation_name (sort keys %$all_operations)
    {
	my $link_target = $all_operations->{$operation_name}->{link_target} || $operation_name;

	my $link = "?project_name=${project_name}&morphology_name=${morphology_name}&operation_name=${link_target}";

	push(@links, $link);
	push(@titles, $all_operations->{$operation_name}->{description} || $operation_name);

	my $icon = $all_operations->{$operation_name}->{icon} || 'images/icon.gif';

	push(@icons, $icon, );
    }

    &icons_table(\@links, \@titles, \@icons);

    print "<hr>" ;

}


sub formalize_operation
{
    my $project_name = shift;

    my $morphology_name = shift;

    my $operation_name = shift;

    my $command = $all_operations->{$operation_name}->{command};

    print "<code>\n";

    print "Executing:\n$command\n";

    print "</code>\n";

    print "<pre>\n";

    my $output = `$command`;

    my $count = ($output =~ tr/\n/\n/);

    print "$count lines of output\n";

    print $output;

    print "</pre>\n";

    print "<hr>" ;

}


sub main
{
    if (!-r $project_root)
    {
	&header('Morphology Browser', "", undef, 1, 1, '', '', '');

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
    elsif (!$morphology_name)
    {
	&header("Morphology Browser: $project_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_morphologies($project_name);

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'}, "/neurospaces_project_browser/?project_name=${project_name}", 'This Project', "/neurospaces_project_browser/", 'All Projects');
    }
    elsif (!$operation_name)
    {
	&header("Morphology Browser: $morphology_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_morphology($project_name, $morphology_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi?project_name=${project_name}", "All Morphologies");
    }
    else
    {
	&header("Morphology Browser: $morphology_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_operation($project_name, $morphology_name, $operation_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi?project_name=${project_name}", "All Morphologies");
    }
}


main();


