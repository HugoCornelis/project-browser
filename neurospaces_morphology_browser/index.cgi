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

my $subproject_name = 'morphologies';

my $morphology_name = $query->param('morphology_name');

my $morphology_name_short = $morphology_name;

if (defined $morphology_name_short)
{
    $morphology_name_short =~ s/.*\///;

    $morphology_name_short =~ s((.*)\..*$)(/$1);
}

my $operation_name = $query->param('operation_name');

my $command_name = $query->param('command_name');


my $all_operations_structured;

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

    my $aggregator_operations
	= {
	   (
	    map
	    {
		/^(.*?)__(.*)$/;

		my $field = $1;

		my $operator = $2;

		$_ => {
		       command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal / --type '^T_sym_segment\$' --reporting-field $field --operator $operator 2>&1",
		       description => "$field $operator of segments",
		      };
	    }
	    qw(
	       DIA__length_average
	       DIA__maximum
	       DIA__minimum
	       SURFACE__cumulate
	       VOLUME__cumulate
	      ),
	   ),
	  };

    my $channel_operations
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
	  };

    my $other_operations
	= {
	   morphology_visualizer => {
				     #! argument to --show is serial for display

				     command => "export DISPLAY=:0.0 && cd '$project_root/$project_name/' && neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --show 2 --protocol none 2>&1",
				     description => "Morphology Visualizer",
				    },
	   morphology_explorer => {
				   #! argument to --show is serial for display

				   command => "export DISPLAY=:0.0 && cd '$project_root/$project_name/' && neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --gui 2>&1",
				   description => "Morphology Explorer",
				  },
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

    $all_operations_structured
	= {
	   aggregator_operations => $aggregator_operations,
	   channel_operations => $channel_operations,
	   other_operations => $other_operations,
	  };

    $all_operations
	= {
	   %$aggregator_operations,
	   %$channel_operations,
	   %$other_operations,
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

    # load module specifics

    use YAML 'LoadFile';

    my $module_description;

    my $module_configuration;

    eval
    {
	$module_configuration = LoadFile("$project_root/$project_name/$subproject_name/configuration.yml");
    };

    my $header = $module_configuration->{description} || 'Morphologies';

    print STDERR "header is $header\n";

    print "<center><h3>$header</h3></center>\n";

    print "<hr>" ;

    # check if a module command was called

    print STDERR "checking for command name\n";

    if ($command_name)
    {
	print STDERR "checking for command name, found $command_name\n";

	# first map the commands to a hash

	my $module_commands = $module_configuration->{commands} || [];

	my $commands
	    = {
	       map
	       {
		   ( $_->{name} => $_->{command} );
	       }
	       @$module_commands,
	      };

	print STDERR "module_commands is:\n" . Dumper($commands);

	# get command to execute

	my $command = $commands->{$command_name};

	$command =~ s/\$project_root/$project_root/g;
	$command =~ s/\$project_name/$project_name/g;

	system "$command &";
    }

    # get all commands specific to this module

    {
	print "<center><h4>Specific Commands</h4></center>\n";

	my @links;
	my @titles;
	my @icons;

	my $module_commands = $module_configuration->{commands} || [];

	foreach my $command (@$module_commands)
	{
	    my $command_name = $command->{name};
	    my $command_description = $command->{description};

	    #    if ($access{$command})
	    {
		push(@links, "?project_name=${project_name}&subproject_name=${subproject_name}&command_name=$command_name");
		push(@titles, $command_description);

		my $icon = 'images/icon.gif';

		push(@icons, $icon, );
	    }
	}

	&icons_table(\@links, \@titles, \@icons);

	print "<hr>" ;
    }

    # get all information from the database

    use Neurospaces::Project::Modules::Morphology 'all_morphologies';

#     my $all_morphologies = [ sort map { chomp; $_; } `find "$project_root/$project_name/morphologies" -name "*.ndf" -o -name "*.p" -o -iname "*.swc"`, ];

    my $all_morphologies
	= all_morphologies
	    (
	     {
	      name => $project_name,
	      root => $project_root,
	     },
	    );

    print "<center><h4>All Available Morphologies</h4></center>\n";

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

    foreach my $operation_group_name (sort keys %$all_operations_structured)
    {
	my $operation_group = $all_operations_structured->{$operation_group_name};

	my @links;
	my @titles;
	my @icons;

	print "<h2>$operation_group_name</h2>" ;

	foreach my $operation_name (sort keys %$operation_group)
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


