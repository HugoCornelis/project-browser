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
		  neurospaces_simulation_browser => {
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


use YAML 'LoadFile';

my $neurospaces_config = LoadFile('/etc/neurospaces/project_browser/project_browser.yml');

my $project_name = $query->param('project_name');

my $subproject_name = $query->param('subproject_name');

my $module_name = $query->param('module_name');

my $ssp_directory = $neurospaces_config->{project_browser}->{root_directory} . "$project_name/$subproject_name/$module_name";


sub document_ssp_schedule
{
    my $scheduler = shift;

    my $schedule_name = shift;

    my $subschedule_name = shift || '';

    my $column_specification;

    my $submitted_request;

#     if (exists $sesa_specification->{column_specifications}->{$subschedule_name}->{column_specification})
#     {
# 	$column_specification = $sesa_specification->{column_specifications}->{$subschedule_name}->{column_specification};

# 	$submitted_request = "column_specification_$subschedule_name";
#     }
#     else
#     {
# 	$column_specification = $sesa_specification->{column_specification};

# 	$submitted_request = 'column-specification';
#     }

#     my $schedules
# 	= {
# 	   map
# 	   {
# 	       $_ => {
# 		      label => $column_specification->{$_}->{description},
# 		      name => $_,
# 		      value => $column_specification->{$_}->{schedules} || '',
# 		     };
# 	   }
# 	   keys %$column_specification,
# 	  };

#     my $order
# 	= {
# 	   map
# 	   {
# 	       $_ => $column_specification->{$_}->{order};
# 	   }
# 	   keys %$column_specification,
# 	  };

#     my $format_schedules
# 	= {
# 	   columns =>
# 	   [
# 	    {
# 	     header => 'Parameter Name',
# 	     key_name => "name",
# 	     type => 'constant',
# 	     be_defined => 1,
# 	    },
# 	    {
# 	     header => 'English Description',
# 	     key_name => "label",
# 	     type => 'constant',
# 	     be_defined => 1,
# 	    },
# 	    {
# 	     header => 'Unit',
# 	     key_name => 'value',
# 	     type => $editable == 2 ? 'textfield' : 'constant',
# 	     be_defined => 1,
# 	     encapsulator => {
# 			      options => { size => 30, maxlength => 80, },
# 			     },
# 	    },
# 	   ],
# 	  };

    my $header = "SSP Schedule $schedule_name";

#     if ($subschedule_name)
#     {
# 	$header .= ", Submodule $subschedule_name";
#     }

#     my $workflow_schedules
# 	= Sesa::Workflow->new
# 	    (
# 	     {
# 	      sequence => [
# 			   {
# 			    label => "Sesa",
# 			    target => '/?cat=sesa',
# 			   },
# 			   {
# 			    label => "Persistency",
# 			    target => '/sems_sesa_persistency_editor/',
# 			   },
# 			   {
# 			    label => "Units",
# 			    target => '/sems_sesa_persistency_editor/units.cgi',
# 			   },
# 			   {
# 			    label => "These",
# 			    target => "/sems_sesa_persistency_editor/units.cgi?schedule_name=$schedule_name",
# 			   },
# 			  ],
# 	      related => [
# 			  {
# 			   label => "Run module $schedule_name",
# 			   target => '/' . specification_get_module_directory( { module => [ $schedule_name, ], }, ),
# 			  },
# 			  {
# 			   label => 'Defaults',
# 			   target => "/sems_sesa_persistency_editor/defaults.cgi?schedule_name=$schedule_name&subschedule_name=$subschedule_name",
# 			  },
# 			  {
# 			   label => 'Labels',
# 			   target => "/sems_sesa_persistency_editor/labels.cgi?schedule_name=$schedule_name&subschedule_name=$subschedule_name",
# 			  },
# 			  {
# 			   label => 'Row Order',
# 			   target => "/sems_sesa_persistency_editor/order.cgi?schedule_name=$schedule_name&subschedule_name=$subschedule_name",
# 			  },
# 			  {
# 			   label => 'Headers',
# 			   target => "/sems_sesa_persistency_editor/heditor.cgi?schedule_name=$schedule_name&subschedule_name=$subschedule_name",
# 			  },
# 			 ],
# 	     },
# 	     {
# 	      self => $ENV{REQUEST_URI},
# 	     },
# 	    );

    my $document_schedules
	= Sesa::TreeDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     column_headers => 1,
	     contents => $scheduler,
# 	     format => $format_schedules,
	     has_submit => $editable == 2,
	     has_reset => $editable == 2,
	     header => $header,
	     hidden => {
			$project_name ? ( project_name => $project_name, ) : (),
			$subproject_name ? ( subproject_name => $subproject_name, ) : (),
			$module_name ? ( module_name => $module_name, ) : (),
		       },
	     name => 'column-specification',
	     output_mode => 'html',
	     regex_encapsulators => [
				     {
				      match_content => 1,
				      name => 'channel-inhibited-editfield-encapsulator',
				      regex => ".*NEW_.*",
				      type => 'constant',
				     },
				    ],
	     row_filter => sub { !ref $_[1]->{value}, },
	     separator => '/',
# 	     sort => sub { return $order->{$_[0]} <=> $order->{$_[1]}; },
# 	     submit_actions => {
# 				'column-specification' =>
# 				sub
# 				{
# 				    my ($document, $request, $contents, ) = @_;

# 				    # merge the new data into the old data

# 				    map
# 				    {
# 					$column_specification->{$_}->{schedules}
# 					    = $contents->{$_}->{value};
# 				    }
# 					keys %$column_specification;

# 				    # write the new content

# 				    specification_write($schedule_name, $scheduler, [ $submitted_request ] );

# 				    return $contents;
# 				},
# 			       },
# 	     workflow => {
# # 			  actor => $workflow_schedules,
# 			  configuration => {
# 					    header => {
# 						       after => 1,
# 						       before => 1,
# # 						       history => 1,
# 						       related => 1,
# 						      },
# 					    trailer => {
# 							after => 1,
# 						       },
# 					   },
# 			 },
	    );

    return [ $document_schedules, ];
}


sub formalize_sesa_schedules_for_module
{
    my $documents = shift;

    documents_formalize($documents, { rulers => 1, }, );
}


sub formalize_ssp_root
{
    my $ssp_directory = shift;

    # get all information from the database

    my $all_schedules = [ sort map { s/^generated__//; s/\.yml$//; $_; } grep { /^generated__/ && /\.yml$/ } map { chomp; $_; } `/bin/ls -1 "$ssp_directory/schedules"`, ];

    my @links;
    my @titles;
    my @icons;

    foreach my $schedule (@$all_schedules)
    {
	#    if ($access{$subschedule})
	{
	    push(@links, "?project_name=${project_name}&subproject_name=${subproject_name}&module_name=${module_name}&schedule_name=${schedule}");
	    push(@titles, $schedule);

	    my $icon = 'images/ssp32x32.png';

	    push(@icons, $icon, );
	}
    }

    &icons_table(\@links, \@titles, \@icons);

    print "<hr>" ;

}


sub main
{
    if (!-r $ssp_directory
	|| !-r "$ssp_directory")
    {
	&header('Simulation Browser and Editor', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<H3>The simulation directory does not exist.</H3>";

	print "<p>\n";

	print "$ssp_directory not found\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
    elsif (!$project_name
	   || !$subproject_name
	   || !$module_name)
    {
	my $url = "/neurospaces_project_browser/?";

	my $args = [];

	foreach my $argument_name (
				   qw(
				      project_name
				      subproject_name
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

	&redirect($url, 'Project Browser');
    }
    else
    {
	my $schedule_name = $query->param('schedule_name');

	if (!defined $schedule_name)
	{
	    my $submodules = do './submodules.pl';

	    &header("SSP Simulation Browser", "", undef, 1, 1, 0, '');

	    print "<hr>\n";

	    formalize_ssp_root($ssp_directory);

	    # finalize (web|user)min specific stuff.

	    &footer("index.cgi", 'SSP Simulation Browser');
	}
	else
	{
	    my $subschedule_name = $query->param('subschedule_name');

	    if (!defined $subschedule_name || $subschedule_name eq '')
	    {
		&header("SSP Schedule: $schedule_name", "", undef, 1, 1, '', '', '');

		print "<hr>\n";

		use YAML;

		my $filename = "generated__$schedule_name.yml";

		my $scheduler;

		eval
		{
		    local $/;

		    $scheduler = Load(`cat "$ssp_directory/schedules/$filename"`);
		};

		if ($@)
		{
		    my $read_error = "$0: scheduler cannot be constructed from '$filename': $@, ignoring this schedule\n";

		    print $read_error;

		    &error($read_error);
		}

		my $documents = document_ssp_schedule($scheduler, $schedule_name, );

		my $data = documents_parse_input($documents);

		documents_merge_data($documents, $data);

		formalize_sesa_schedules_for_module($documents);

		# finalize (web|user)min specific stuff.

		&footer("index.cgi", 'SSP Simulation Browser');
	    }
	    else
	    {
		&header("Unit Editor", "", undef, 1, 1, '', '', '');

		print "<hr>\n";

		my ($sesa_specification, $read_error) = specification_read($schedule_name);

		if ($read_error)
		{
		    &error($read_error);
		}

		my $documents = document_ssp_schedule($sesa_specification, $schedule_name, $subschedule_name, );

		my $data = documents_parse_input($documents);

		documents_merge_data($documents, $data);

		formalize_sesa_schedules_for_module($documents);

		# finalize (web|user)min specific stuff.

		&footer("index.cgi", 'Persistency Layer Editors', "schedules.cgi", 'Schedule Editor', "schedules.cgi?project_name=${project_name}&subproject_name=${subproject_name}&module_name=${module_name}&schedule_name=${schedule_name}", ${schedule_name});
	    }
	}
    }
}


main();


