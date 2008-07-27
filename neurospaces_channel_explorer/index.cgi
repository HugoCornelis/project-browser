#!/usr/bin/perl -w
#!/usr/bin/perl -d:ptkdb -w
#
# Copyright (C) 2007-2008 Hugo Cornelis, hugo.cornelis@gmail.com
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

my $project_name = $query->param('project_name');

my $subproject_name = $query->param('subproject_name');

my $channel_name = $query->param('channel_name');

my $project_root = $neurospaces_config->{project_browser}->{root_directory};

my $figures_directory = $neurospaces_config->{project_browser}->{root_directory} . "$project_name/$subproject_name/channel-explorer/figures";


sub formalize_project
{
    my $project_name = shift;

    my $subproject_name = shift;

    use YAML;

    # get all information from the database

    my $all_channels_configuration = YAML::LoadFile("$project_root/$project_name/$subproject_name/configuration.yml");

    my @links;
    my @titles;
    my @icons;

    my $all_channels = $all_channels_configuration->{channels};

    foreach my $channel_name (keys %$all_channels)
    {
	my $channel = $all_channels->{$channel_name};

	use YAML 'LoadFile';

	my $channel_description = $channel->{description};

	#    if ($access{$subschedule})
	{
	    push(@links, "?project_name=${project_name}&subproject_name=${subproject_name}&channel_name=${channel_name}");
	    push(@titles, $channel_description);

	    my $icon = 'images/icon.gif';

	    push(@icons, $icon, );
	}
    }

    &icons_table(\@links, \@titles, \@icons);

    print "<hr>" ;

}


sub formalize_project_channel
{
    my $project_name = shift;

    my $subproject_name = shift;

    my $channel_name = shift;

    use YAML;

    # get all information from the database

    my $all_channels_configuration = YAML::LoadFile("$project_root/$project_name/$subproject_name/configuration.yml");

    my $all_channels = $all_channels_configuration->{channels};

    # obtain information about the requested channel

    my $channel = $all_channels->{$channel_name};

    my $channel_model_specification = $channel->{model};

    $channel_model_specification =~ /(.*)::(.*)/;

    my $channel_modelfile = $1;

    my $modelname = $2;

    # define a schedule to extract the tables

    $ENV{NEUROSPACES_NMC_SYSTEM_MODELS} = "/usr/local/neurospaces/models/library";

    use SSP;

    my $args = [ "$0", "-P", $channel_modelfile ];

    my $scheduler
	= SSP->new(
		   {
		    apply => {
			      simulation => [
					     {
					      arguments => [
							    {
# 							     format => 'alpha-beta',
							     format => 'steadystate-tau',
# 							     format => 'A-B',
# 							     format => 'internal',
							     output => 'file:///tmp/a',
							     source => "$modelname/segments/soma/naf/naf_gate_activation/A",
							    },
							   ],
					      method => 'dump',
					      object => 'tabulator',
					     },
					     {
					      arguments => [
							    {
# 							     format => 'alpha-beta',
							     format => 'steadystate-tau',
# 							     format => 'A-B',
# 							     format => 'internal',
							     output => 'file:///tmp/b',
							     source => "$modelname/segments/soma/naf/naf_gate_activation/B",
							    },
							   ],
					      method => 'dump',
					      object => 'tabulator',
					     },
					    ],
			     },
		    analyzers => {
				  tabulator => {
						module_name => 'Heccer',
						package => 'Heccer::Tabulator',
						initializers => [
								 {
								  arguments => [ { source => "neurospaces::$modelname", }, ],
								  method => 'serve',
								 },
								],
					       },
				 },
		    models => [
			       {
				modelname => $modelname,
				solverclass => "heccer",
			       },
			      ],
		    name => "tabulator for $modelname",
		    services => {
				 neurospaces => {
						 initializers => [
								  {
								   arguments => [ $args, ],
								   method => 'read',
								  },
								 ],
# 						 model_library => '/usr/local/neurospaces/models/library',
						 module_name => 'Neurospaces',
						},
				},
		    solverclasses => {
				      heccer => {
# 						 constructor_settings => {
# 									  configuration => {
# 											    reporting => {
# 													  granularity => 10000,
# 													  tested_things => (
# 															    $SwiggableHeccer::HECCER_DUMP_VM_COMPARTMENT_MATRIX
# 															    | $SwiggableHeccer::HECCER_DUMP_VM_COMPARTMENT_DATA
# 															    | $SwiggableHeccer::HECCER_DUMP_VM_COMPARTMENT_OPERATIONS
# 															    | $SwiggableHeccer::HECCER_DUMP_VM_MECHANISM_DATA
# 															    | $SwiggableHeccer::HECCER_DUMP_VM_MECHANISM_OPERATIONS
# 															    | $SwiggableHeccer::HECCER_DUMP_VM_SUMMARY
# 															   ),
# 													 },
# 											   },
# 									  dStep => 5e-7,
# 									  options => {
# 										      iIntervalEntries => 10,
# 										     },
# 									 },
						 module_name => 'Heccer',
						 service_name => 'neurospaces',
						},
				     },
		   },
		  );

    # get the tables

    my $channel_tables = $scheduler->run();

    # visualize the tables

    my $tables_a = YAML::LoadFile("/tmp/a");
    my $tables_b = YAML::LoadFile("/tmp/b");

    my $steady_state = $tables_a->{steady};

    my $tau = $tables_a->{tau};

    {
# 	use GD;

# 	my $graph = GD::Image->new(400, 300);

# 	my $white = $graph->colorAllocate(255,255,255);

# 	$graph->transparent($white);

# 	print $graph->png();

	use File::Temp qw/ :mktemp /;

	use Math::Trig qw [pi];

	use PDL;
	use PDL::Graphics::PLplot;

	# get a temporary file

	#t note that this is an unsafe implementation

	my $filename_pbm = mktemp("../tmp/neurospaces_output_pbm_XXXXXXXXXXXX");

	#! needed for mime types below, here needed for consistency

	$filename_pbm .= ".pbm";

	my $units
	    = {
	       'Ca' => 'mol',
	       'Gk' => 'Siemens',
	       'Ik' => 'Current',
	       'Vm' => 'Vm',
	       'state_x' => 'prob.',
	       'state_y' => 'prob.',
	      };

	my $unit = $units->{''} || 'state';

	my $pl
	    = PDL::Graphics::PLplot->new
		(
		 DEV => "pbm",
		 FILE => $filename_pbm,
		 PAGESIZE => [ 1000, 900, ],
		 XLAB => 'Vm',
		 YLAB => $unit,
		);

# 	#! + 1 for time step

# 	my $output_filename = $figures_directory . "/generated__" . $channel_name;

# 	@$columns = PDL->rcols($output_filename, 0, $column);

	# add the extracted columns to the plot

	my $range
	    = [
	       map
	       {
		   $tables_a->{hi}->{start} + $_ * $tables_a->{hi}->{step};
	       }
	       1 .. $tables_a->{entries},
	      ];

	$pl->xyplot($range, $tau);

	$pl->close();

	my $filename_png = mktemp("../tmp/neurospaces_output_png_XXXXXXXXXXXX");

	$filename_png .= ".png";

	system "convert \"$filename_pbm\" \"$filename_png\"";

	if ($?)
	{
	    print STDERR "system operator error: $?\n";
	}

	&header("Channel Kinetics Plotter: $channel_name", "", undef, 1, 1, '', '', '');

	print "<hr>\n";

# 	my $documents = document_ssp_schedule($sesa_specification, $schedule_name, $output_name, );

# 	my $data = documents_parse_input($documents);

# 	documents_merge_data($documents, $data);

# 	formalize_sesa_outputs_for_module($documents);

	print "<center>\n";

	print "<img src=\"$filename_png\" alt=\"a plplot image\" border=0>\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("index.cgi?project_name=${project_name}&subproject_name=${subproject_name}", "Project $project_name, $subproject_name");
    }
}


sub main
{
    if (!-r $project_root)
    {
	&header('Project Browser and Editor', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<H3>The projects directory does not exist.</H3>";

	print "<p>\n";

	print "$project_root not found\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
    elsif (!$project_name)
    {
	&header("Project Browser: All Projects", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_project_root();

	# finalize (web|user)min specific stuff.

	&footer("index.cgi", 'Project Browser');
    }
    elsif (!$subproject_name)
    {
	&header("Project Browser: $project_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_project_subprojects($project_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi", 'All Projects');
    }
    elsif (!$channel_name)
    {
	&header("Project Browser: $project_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_project($project_name, $subproject_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi?project_name=${project_name}", "Project $project_name");
    }
    else
    {
	&header("Project Browser: $project_name", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	formalize_project_channel($project_name, $subproject_name, $channel_name);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi?project_name=${project_name}&subproject_name=${subproject_name}", "Project $project_name, $subproject_name");
    }
}


main();


