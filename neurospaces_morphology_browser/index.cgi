#!/usr/bin/perl -w
#!/usr/bin/perl -d:ptkdb -w
#
# Copyright (C) 2007-2008 Hugo Cornelis, hugo.cornelis@gmail.com
#


use strict;


use CGI;

use Carp;

$SIG{__DIE__}
    = sub {

	confess(@_);

    };

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
						     label => 'morphology analysis',
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

my $module_name = $query->param('module_name');

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
    my $aggregator_operations
	= {
	   (
	    map
	    {
		/^(.*?)__(.*)$/;

		my $field = $1;

		my $operator = $2;

		$_ => {
		       command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --no-use-library --traversal / --type '^T_sym_segment\$' --reporting-field $field --operator $operator 2>&1",
		       description => "$field $operator of segments",
		      };
	    }
	    qw(
	       DIA__length_average
	       DIA__maximum
	       DIA__minimum
	       LENGTH__cumulate
	       SURFACE__cumulate
	       VOLUME__cumulate
	      ),
	   ),
	  };

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

    my $structure_operations
	= {
	   average_diameter => {
				command =>
				sub
				{
				    #t need stddev.

				    use Neurospaces::Morphology;

				    my $morphology
					= Neurospaces::Morphology->new
					    (
					     {
					      backend_options => [ '-A', ],
					      filename => "$project_root/$project_name/morphologies/$morphology_name",
					     },
					    );

				    my $average_diameter = $morphology->average_diameter($morphology_name_short);

				    return { average_diameter => $average_diameter, };
				},
				description => "Average dendritic diameter",
			       },
	   branchpoints => {
			    command =>
			    sub
			    {
				use Neurospaces::Morphology;

				my $morphology
				    = Neurospaces::Morphology->new
					(
					 {
					  backend_options => [ '-A', ],
					  filename => "$project_root/$project_name/morphologies/$morphology_name",
					 },
					);

				my $branchpoints = $morphology->branchpoints($morphology_name_short);

				return { branchpoints => $branchpoints, };
			    },
			    description => "Branchpoints",
			   },
	   tips => {
		    command => "echo 'segmentertips $morphology_name_short' | neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --query 2>&1",
		    description => "Dendritic tips",
		   },
	   tips2 => {
		     command =>
		     sub
		     {
			 use Neurospaces::Morphology;

			 my $morphology
			     = Neurospaces::Morphology->new
				 (
				  {
				   backend_options => [ '-A', ],
				   filename => "$project_root/$project_name/morphologies/$morphology_name",
				  },
				 );

			 my $tips = $morphology->dendritic_tips($morphology_name_short);

 			 return { summary => $tips->{linearize} , tips => $tips->{tips}->{names}, };
		     },
		     description => "Dendritic tips2",
		    },
	   tip_lengths => {
			   command =>
			   sub
			   {
			       use Neurospaces::Morphology;

			       my $morphology
				   = Neurospaces::Morphology->new
				       (
					{
					 backend_options => [ '-A', ],
					 filename => "$project_root/$project_name/morphologies/$morphology_name",
					},
				       );

			       my $tip_lengths = $morphology->tip_lengths($morphology_name_short);

			       return { tip_lengths => $tip_lengths, };
			   },
			   description => "Tip lengths",
			  },
	  };

    my $structure_summary_operations
	= {
	   structure_summary_operations_all => {
						command =>
						sub
						{
						    use Neurospaces::Morphology;

						    my $morphology
							= Neurospaces::Morphology->new
							    (
							     {
							      backend_options => [ '-A', ],
							      filename => "$project_root/$project_name/morphologies/$morphology_name",
							     },
							    );

						    my $average_diameter = $morphology->average_diameter($morphology_name_short);

						    my $branchpoints = $morphology->branchpoints($morphology_name_short);

						    my $average_branchpoints_per_tip = $morphology->average_branchpoints_per_tip($morphology_name_short);

						    my $tips = $morphology->dendritic_tips($morphology_name_short);

						    my $average_tip_lengths = $morphology->average_tip_lengths($morphology_name_short);

						    my $total_surface_area = $morphology->total_surface_area($morphology_name_short);
						    my $total_volume = $morphology->total_volume($morphology_name_short);
						    my $total_length = $morphology->total_length($morphology_name_short);

						    return
						    {
# 						     1 => $morphology,
						     average_diameter => $average_diameter,
						     average_tip_lengths => $average_tip_lengths,
						     branchpoints => scalar keys %$branchpoints,
						     average_branchpoints_per_tip => $average_branchpoints_per_tip,
# 						     tips => $tips,
						     total_length => $total_length,
						     total_surface_area => $total_surface_area,
						     total_volume => $total_volume,
						    };
						},
						description => 'Summary of the cell structure',
					       },
	  };

    my $other_operations
	= {
	   morphology_visualizer => {
				     #! argument to --show is serial for display

				     command => "export DISPLAY=:0.0 && cd '$project_root/$project_name/' && neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --show 2 --protocol none 2>&1",
				     description => "Morphology Visualizer",
				    },
	   morphology_explorer_activated => {
					     command => "export DISPLAY=:0.0 && cd '$project_root/$project_name/' && neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --gui 2>&1",
					     description => "Morphology Explorer, Activated Morphology",
					    },
	   morphology_explorer_passive => {
					   command => "export DISPLAY=:0.0 && cd '$project_root/$project_name/' && neurospaces '$project_root/$project_name/morphologies/$morphology_name' --no-use-library --gui 2>&1",
					   description => "Morphology Explorer, Passive Morphology",
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
				       command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal / --type '^T_sym_segment\$' --condition '\$d->{context} !~ /_spine/i && SwiggableNeurospaces::symbol_parameter_resolve_value(\$d->{_symbol}, \$d->{_context}, \"DIA\") < 3.18e-6' --reporting-field LENGTH --operator cumulate 2>&1",
				       description => "Cumulated spiny compartment lengths",
				      },
	   somatopetals => {
			    command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal-symbol / --reporting-field SOMATOPETAL_DISTANCE --type segment 2>&1",
			    description => "Somatopetal Lengths",
			   },
	   surface_spiny_cumulated => {
				       command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --traversal / --type '^T_sym_segment\$' --condition '\$d->{context} !~ /_spine/i && SwiggableNeurospaces::symbol_parameter_resolve_value(\$d->{_symbol}, \$d->{_context}, \"DIA\") < 3.18e-6' --reporting-field SURFACE --operator cumulate 2>&1",
				       description => "Cumulated spiny compartment surface",
				      },
	   spines => {
		      command => "neurospaces '$project_root/$project_name/morphologies/$morphology_name' --force-library --algorithm Spines 2>&1",
		      description => "Spines instance algorithm",
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
	   aggregator_operations => {
				     description => 'operations that operate on the whole morphology',
				     operations => $aggregator_operations,
				     priority => 20,
				    },
	   channel_operations => {
				  description => 'operations that report on channel distribution',
				  operations => $channel_operations,
				  priority => 30,
				 },
	   other_operations => {
				description => 'other operations',
				operations => $other_operations,
				priority => 40,
			       },
	   structure_operations => {
				    description => 'detailed operations that quantify the morphology structure',
				    operations => $structure_operations,
				    priority => 10,
				   },
	   structure_summary_operations => {
					    description => 'operations that quantify the morphology structure',
					    operations => $structure_summary_operations,
					    priority => 5,
					   },
	  };

    $all_operations
	= {
	   %$aggregator_operations,
	   %$channel_operations,
	   %$other_operations,
	   %$structure_operations,
	   %$structure_summary_operations,
	  };

    # get project local information

    #t should be in a subdirectory and depend on the cgi $query params ?

    use YAML 'LoadFile';

    eval
    {
	$all_operations ||= LoadFile("$project_root/$project_name/morphologies/descriptor.yml");
    };

}


sub document_morphologies
{
    my $project_name = shift;

    # load module specifics

    use YAML 'LoadFile';

    my $module_description;

    my $module_configuration;

    eval
    {
	$module_configuration = LoadFile("$project_root/$project_name/$subproject_name/descriptor.yml");
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

    # get all commands specific to this module and project

    {
	print "<center><h4>Commands Specific to this Project Module</h4></center>\n";

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

    use Neurospaces::Project::Modules::Morphology 'morphology_groups_read';

    my $all_morphology_groups
	= morphology_groups_read
	    (
	     {
	      name => $project_name,
	      root => $project_root,
	     },
	    );

#     my $all_groups = $all_morphology_groups->{groups};

    my $format_morphology_groups
	= {
	   columns =>
	   [
	    {
	     be_defined => 1,
	     header => 'Morphology Group',
	     key_name => 'dummy1',
	     type => 'constant',
	    },
	    {
	     be_defined => 1,
	     encapsulator => {
			      options => {
					  -maxlength => 30,
					  -size => 35,
					 },
			     },
	     header => 'Description',
	     key_name => 'description',
	     type => 'textfield',
	    },
	    {
	     be_defined => 1,
	     header => 'Group Number',
	     key_name => 'number',
	     type => 'constant',
	    },
	    {
	     be_defined => 1,
	     generate =>
	     sub
	     {
		 my $self = shift;

		 my $group_name = shift;

		 my $group = shift;

		 my $cell_value = shift;

		 if ($editable)
		 {
		     return
			 $query->submit
			     (
			      -name  => "delete_$self->{name}_$group->{number}",
			      -value => ' Delete ',
			      (!$cell_value ? (-disabled => 1) : ()),
			     );
		 }
		 else
		 {
		     return "&nbsp;";
		 }
	     },
	     header => 'Add / Delete',
	     key_name => 'can be deleted',
	     type => 'code',
	    },
	    {
	     be_defined => 1,
	     generate =>
	     sub
	     {
		 my $self = shift;

		 my $row_key = shift;

		 my $row = shift;

		 my $filter_data = shift;

		 my $str = '';

		 $str
		     .= $query->a
			 (
			  {
			   -href => $row->{link},
			  },
			  "Analyze",
			 );

		 return($str);
	     },
	     header => 'Operation 1',
	     key_name => 'operation 1',
	     type => 'code',
	    },
	   ],
	   hashkey => 'Morphology Group',
	  };

    my $session_id_digest = $query->param('session_id');

    if (!defined $session_id_digest)
    {
	my $session_id = rand(10000);

	use Digest::SHA1 'sha1_base64';

	$session_id_digest = sha1_base64($session_id);
    }

    my $workflow_morphology_groups
	= Sesa::Workflow->new
	    (
	     {
	      sequence => [
			   {
			    label => "Neurospaces",
			    target => '/?cat=neurospaces',
			   },
			   {
			    label => "Outputs",
			    target => '/neurospaces_output_browser/',
			   },
			  ],
	      related => [
			  {
			   label => "Simulation Generator",
			   target => '/neurospaces_simulation_generator/',
			  },
			  {
			   label => "Simulation Browser",
			   target => '/neurospaces_simulation_browser/',
			  },
			 ],
	     },
	     {
	      self => $ENV{REQUEST_URI},
	     },
	    );

    my $document_morphology_groups
	= Sesa::TableDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     column_headers => 1,
	     contents => $all_morphology_groups->{groups},
	     format => $format_morphology_groups,
	     has_submit => $editable,
	     has_reset => $editable,
	     header => '<h2> Morphology Groups </h2>
<h4> Analyze morphology group characteristics. </h4>',
	     hidden => {
			session_id => $session_id_digest,
			$project_name ? ( project_name => $project_name, ) : (),
			$subproject_name ? ( subproject_name => $subproject_name, ) : (),
			$module_name ? ( module_name => $module_name, ) : (),
		       },
	     name => 'morphology-groups',
	     output_mode => 'html',
	     regex_encapsulators => [
				     {
				      match_content => 1,
				      name => 'channel-inhibited-editfield-encapsulator',
				      regex => ".*NEW_.*",
				      type => 'constant',
				     },
				    ],
# 	     row_filter => sub { !ref $_[1]->{value}, },
	     row_finalize =>
	     sub
	     {
		 my $self = shift;

		 my $result = '';

		 if ($editable)
		 {
		     $self->set_not_empty();

		     $result .= "<tr $main::cb>" ;

		     $result .= "<td align='center'>";
		     $result .= $query->textfield(
						  -name      => "field$self->{separator}$self->{name}_add_group-name",
						  -default   => '',
						  -override  => 1,
						  -size      => 35,
						  -maxlength => 30,
						 );
		     $result .= "</td>";

		     $result .= "<td style='border-left-style: hidden'></td>";

		     $result .= "<td align='center'>";
		     $result .= $query->textfield(
						  -name      => "field$self->{separator}$self->{name}_add_group-description",
						  -default   => '',
						  -override  => 1,
						  -size      => 35,
						  -maxlength => 30,
						 );
		     $result .= "</td>";

		     $result .= "<td style='border-left-style: hidden'></td>";

		     $result .= "<td align='center'>";
		     $result .= (scalar keys %{$all_morphology_groups->{groups}}) + 1;
		     $result .= "</td>";

		     $result .= "<td style='border-left-style: hidden'></td>";

#  		     my $columns = 2 * $#{$format_morphology_groups->{columns}} - 4;

# 		     $result .= "<td align='center' colspan='$columns'>";

		     $result .= "<td align='center'>";

		     $result
			 .= $query->submit(
					   -name  => "add_morphology-group_$self->{name}",
					   -value => ' Add ',
					  );
		     $result .= "</td>";

		     $result .= "<td style='border-left-style: hidden'></td>";

		     foreach my $column_format (4 .. $#{$format_morphology_groups->{columns}})
		     {
			 $result .= "<td align='center'>";

			 $result .= "&nbsp;";

			 $result .= "</td>";

			 $result .= "<td style='border-left-style: hidden'></td>";

		     }

		     $result .= "</tr>\n";

		 }

		 return($result);
	     },
	     separator => '/',
	     sort => sub { return $_[2]->{number} <=> $_[3]->{number} },
	     workflow => {
			  actor => $workflow_morphology_groups,
			  configuration => {
					    header => {
						       after => 1,
						       before => 1,
# 						       history => 1,
						       related => 1,
						      },
					    trailer => {
							after => 1,
						       },
					   },
			 },
	    );

    # get all information from the database

    use Neurospaces::Project::Modules::Morphology 'morphologies_read';

    my $all_morphologies
	= morphologies_read
	    (
	     {
	      name => $project_name,
	      root => $project_root,
	     },
	    );

#     print "<center><h4>All Available Morphologies</h4></center>\n";

    my $rows;

    foreach my $morphology_name (@$all_morphologies)
    {
	$morphology_name =~ s(^$project_root/$project_name/morphologies)();

	use YAML 'LoadFile';

	my $morphology_description;

	my $module_configuration;

	eval
	{
	    $module_configuration = LoadFile("$project_root/$project_name/morphologies/$morphology_name/descriptor.yml");
	};

	$morphology_description = $module_configuration->{description} || $morphology_name;

	$rows->{$morphology_name}
	    = {
	       (
		map
		{
		    my $group_number = $_;

		    my $group_names
			= [
			   grep
			   {
			       $all_morphology_groups->{groups}->{$_}->{number} eq $group_number
			   }
			   keys %{$all_morphology_groups->{groups}},
			  ];

		    if ($#$group_names ne 0)
		    {
			die "$0: group_names inconsistency, group_names is $#$group_names";
		    }

		    my $group_name = $group_names->[0];

		    (
		     "group$group_number" => ( $all_morphology_groups->{groups}->{$group_name}->{morphologies}->{$morphology_name} ? 1 : 0),
		    );
		}
		1 .. scalar keys %{$all_morphology_groups->{groups}},
	       ),
	       link => "?project_name=${project_name}&morphology_name=${morphology_name}",
# 	       title => $morphology_description,
	      };
    }

    my $format_morphologies
	= {
	   columns =>
	   [
	    {
	     header => 'Morphology',
	     key_name => 'dummy1',
	     type => 'constant',
	     be_defined => 1,
	    },
	    {
	     header => 'Analyze',
	     key_name => 'link',
	     type => 'code',
	     be_defined => 1,
	     generate =>
	     sub
	     {
		 my $self = shift;

		 my $row_key = shift;

		 my $row = shift;

		 my $filter_data = shift;

		 my $result = '';

		 $result
		     .= $query->a
			 (
			  {
			   -href => $row->{link},
			  },
			  "Analyze",
			 );

		 return($result);
	     },
	    },
	    map
	    {
		my $group_name = $_;

		(
		 {
		  header => $group_name,
		  key_name => 'group' . $all_morphology_groups->{groups}->{$group_name}->{number},
		  type => 'checkbox',
		  be_defined => 1,
# 		  generate =>
# 		  sub
# 		  {
# 		      my $self = shift;

# 		      my $row_key = shift;

# 		      my $row = shift;

# 		      my $filter_data = shift;

# 		      if ($editable)
# 		      {
# 			  my $result = '';

# 			  print STDERR Dumper(\@_);

# 			  my $default = $row->{group};

# 			  my $value = [ 'None', 0 .. 10 ];

# 			  my $name = "field$self->{separator}$self->{name}_configuration_${row_key}_1";

# 			  $result
# 			      .= $query->popup_menu
# 				  (
# 				   -name => $name,
# 				   -default => $default,
# 				   -values => $value,
# 				   -override => 1,
# 				  );

# 			  return($result);
# 		      }
# 		      else
# 		      {
# 			  return "Undefined";
# 		      }
# 		  },
		 }
		);
	    }
	    keys %{$all_morphology_groups->{groups}},
	   ],
	   hashkey => 'Morphology',
	  };

    my $workflow_morphologies
	= Sesa::Workflow->new
	    (
	     {
	      sequence => [
			   {
			    label => "Neurospaces",
			    target => '/?cat=neurospaces',
			   },
			   {
			    label => "Outputs",
			    target => '/neurospaces_output_browser/',
			   },
			  ],
	      related => [
			  {
			   label => "Simulation Generator",
			   target => '/neurospaces_simulation_generator/',
			  },
			  {
			   label => "Simulation Browser",
			   target => '/neurospaces_simulation_browser/',
			  },
			 ],
	     },
	     {
	      self => $ENV{REQUEST_URI},
	     },
	    );

    my $document_morphologies
	= Sesa::TableDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     column_headers => 1,
	     contents => $rows,
	     format => $format_morphologies,
	     has_submit => $editable,
	     has_reset => $editable,
	     header => '<h2> Morphology Names </h2>
<h4> Define morphology groups, then submit for further analysis. </h4>',
	     hidden => {
			session_id => $session_id_digest,
			$project_name ? ( project_name => $project_name, ) : (),
			$subproject_name ? ( subproject_name => $subproject_name, ) : (),
			$module_name ? ( module_name => $module_name, ) : (),
		       },
	     name => 'morphologies',
	     output_mode => 'html',
	     regex_encapsulators => [
				     {
				      match_content => 1,
				      name => 'channel-inhibited-editfield-encapsulator',
				      regex => ".*NEW_.*",
				      type => 'constant',
				     },
				    ],
# 	     row_filter => sub { !ref $_[1]->{value}, },
	     separator => '/',
	     sort => sub { return $_[0] cmp $_[1] },
	     submit_actions => {
				'morphologies' =>
				sub
				{
				    my ($document, $request, $contents, ) = @_;

				    use YAML 'LoadFile';

				    # loop over all groups

				    use Neurospaces::Project::Modules::Morphology 'morphology_groups_read', 'morphology_groups_write';

				    my $all_morphology_groups
					= morphology_groups_read
					    (
					     {
					      name => $project_name,
					      root => $project_root,
					     },
					    );

				    my $all_groups = $all_morphology_groups->{groups};

				    foreach my $group_name (keys %$all_groups)
				    {
					my $group = $all_groups->{$group_name};

					# loop over all morphologies

					use Neurospaces::Project::Modules::Morphology 'morphologies_read';

					my $all_morphologies
					    = morphologies_read
						(
						 {
						  name => $project_name,
						  root => $project_root,
						 },
						);

					foreach my $morphology_name (@$all_morphologies)
					{
					    #t some hacking required because morphologies have not a proper id yet.

					    $morphology_name =~ s/^.*morphologies//;

					    # set in the group descriptor

					    $group->{morphologies}->{$morphology_name} = $contents->{$morphology_name}->{"group" . $group->{number}};
					}
				    }

# 				    # merge the new data into the old data

# 				    map
# 				    {
# 					$column_specification->{$_}->{outputs}
# 					    = $contents->{$_}->{value};
# 				    }
# 					keys %$column_specification;

# 				    # write the new content

# 				    specification_write($module_name, $scheduler, [ $submitted_request ] );

				    my $error
					= morphology_groups_write
					    (
					     {
					      name => $project_name,
					      root => $project_root,
					     },
					     $all_morphology_groups,
					    );

				    return $contents;
				},
			       },
	     workflow => {
			  actor => $workflow_morphologies,
			  configuration => {
					    header => {
						       after => 1,
						       before => 1,
# 						       history => 1,
						       related => 1,
						      },
					    trailer => {
							after => 1,
						       },
					   },
			 },
	    );

    return [ $document_morphology_groups, $document_morphologies, ];

#     print "<hr>" ;

}


sub formalize_morphologies
{
    my $documents = shift;

    documents_formalize($documents, { rulers => 1, }, );
}


sub formalize_morphology
{
    my $project_name = shift;

    my $morphology_name = shift;

    foreach my $operation_group_name (sort
				      {
					  $all_operations_structured->{$a}->{priority} <=> $all_operations_structured->{$b}->{priority}
				      }
				      keys %$all_operations_structured)
    {
	my $operation_group = $all_operations_structured->{$operation_group_name}->{operations};

	my @links;
	my @titles;
	my @icons;

	print "
<center>
<h2>$operation_group_name</h2>
$all_operations_structured->{$operation_group_name}->{description}
</center>
" ;

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

    if ($command =~ m'CODE')
    {
	my $result = &$command();

	print "<pre>\n";

	use YAML;

	print Dump($result);

	print "</pre>\n";

	print "<hr>" ;
    }
    else
    {
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

	my $documents = document_morphologies($project_name);

	my $data = documents_parse_input($documents);

	documents_merge_data($documents, $data);

	formalize_morphologies($documents);

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


