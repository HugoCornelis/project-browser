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
		  neurospaces_output_browser => {
						 level => (our $editable = 1 && \$editable),
						 label => 'simulation output',
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

my $subproject_name = $query->param('subproject_name');

my $module_name = $query->param('module_name');

my $command_name = $query->param('command_name');

my $ssp_directory = $project_root . "$project_name/$subproject_name/$module_name";


sub document_output_root
{
    my $ssp_directory = shift;

    # load module specifics

    use YAML 'LoadFile';

    my $module_description;

    my $module_configuration;

    eval
    {
	$module_configuration = LoadFile("$project_root/$project_name/$subproject_name/$module_name/configuration.yml");
    };

    my $header = $module_configuration->{description} || $module_name;

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
		push(@links, "?project_name=${project_name}&subproject_name=${subproject_name}&module_name=${module_name}&command_name=$command_name");
		push(@titles, $command_description);

		my $icon = 'images/icon.gif';

		push(@icons, $icon, );
	    }
	}

	&icons_table(\@links, \@titles, \@icons);

	print "<hr>" ;
    }

    # get all information from the database

    my $output_modules = [ sort map { s/^generated__//; $_; } grep { /^generated__/ } map { chomp; $_; } `/bin/ls -1 "$ssp_directory/output"`, ];

    # spread the outputs over a grid

    my $grid
	= [
	   map
	   {
	       [
		split '__',
	       ];
	   }
	   @$output_modules,
	  ];

    print STDERR "grid is:\n" . Dumper($grid);

    # get the unique elements of the grid

    my $transposed = [];

    my $row_index = 0;

    foreach my $row (@$grid)
    {
	my $column_index = 0;

	foreach my $column (@$row)
	{
	    $transposed->[$column_index]->[$row_index] = $grid->[$row_index]->[$column_index];

	    $column_index++;
	}

	$row_index++;
    }

    print STDERR "transposed is:\n" . Dumper($transposed);

    my $uniques
	= [
	   map
	   {
	       [
		Sesa::Sems::unique sort @$_,
	       ];
	   }
	   @$transposed,
	  ];

    # remove known protocol names

    my $known_protocols = [ 'conceptual_parameters', 'current', ];

    my $used_protocols = $uniques->[1];

    map
    {
	foreach my $known_protocol (@$known_protocols)
	{
	    s/^${known_protocol}_//;
	}
    }
	@$used_protocols;

    # now add all selectors

    foreach my $unique (@$uniques)
    {
	unshift @$unique, 'All';
    }

    print STDERR "uniques is:\n" . Dumper($uniques);

    my $format_output_selector
	= {
	   columns =>
	   [
	    {
	     header => 'Models',
	     key_name => 'dummy1',
	     type => 'code',
	     be_defined => 1,
	     generate =>
	     sub
	     {
		 my $self = shift;

		 my $row_key = shift;

		 my $row = shift;

		 my $filter_data = shift;

		 if ($editable)
		 {
		     my $str = '';

		     print STDERR Dumper(\@_);

		     my $value = $row->[0];

		     my $name = "field_$self->{name}_configuration_${row_key}_0";

		     my $default = $query->param($name);

		     if (!defined $default)
		     {
			 $default = $value->[0];
		     }

		     $str
			 .= $query->popup_menu
			     (
			      -name => $name,
			      -default => $default,
			      -values => $value,
			      -override => 1,
			     );

		     return($str);
		 }
		 else
		 {
		     return "No models found";
		 }
	     },
	    },
	    {
	     header => 'Protocols',
	     key_name => 'dummy2',
	     type => 'code',
	     be_defined => 1,
	     generate =>
	     sub
	     {
		 my $self = shift;

		 my $row_key = shift;

		 my $row = shift;

		 my $filter_data = shift;

		 if ($editable)
		 {
		     my $str = '';

		     print STDERR Dumper(\@_);

		     my $value = $row->[1];

		     my $name = "field_$self->{name}_configuration_${row_key}_1";

		     my $default = $query->param($name);

		     if (!defined $default)
		     {
			 $default = $value->[0];
		     }

		     $str
			 .= $query->popup_menu
			     (
			      -name => $name,
			      -default => $default,
			      -values => $value,
			      -override => 1,
			     );

		     return($str);
		 }
		 else
		 {
		     return "No protocols found";
		 }
	     },
	    },
	   ],
	   hashkey => 'none',
	  };

    my $session_id_digest = $query->param('session_id');

    if (!defined $session_id_digest)
    {
	my $session_id = rand(10000);

	use Digest::SHA1 'sha1_base64';

	$session_id_digest = sha1_base64($session_id);
    }

    my $workflow_output_selector
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

    my $document_output_selector
	= Sesa::TableDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     column_headers => 1,
	     contents => { content => $uniques, },
	     format => $format_output_selector,
	     has_submit => $editable,
	     has_reset => $editable,
	     header => 'Output Selections
<h4> Select a model and protocol, then submit. </h4>',
	     hidden => {
			session_id => $session_id_digest,
			$project_name ? ( project_name => $project_name, ) : (),
			$subproject_name ? ( subproject_name => $subproject_name, ) : (),
			$module_name ? ( module_name => $module_name, ) : (),
		       },
	     name => 'output-selector',
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
# 	     sort => sub { return $order->{$_[0]} <=> $order->{$_[1]}; },
# 	     submit_actions => {
# 				'output-selector' =>
# 				sub
# 				{
# 				    my ($document, $request, $contents, ) = @_;

# 				    # merge the new data into the old data

# 				    map
# 				    {
# 					$column_specification->{$_}->{outputs}
# 					    = $contents->{$_}->{value};
# 				    }
# 					keys %$column_specification;

# 				    # write the new content

# 				    specification_write($module_name, $scheduler, [ $submitted_request ] );

# 				    return $contents;
# 				},
# 			       },
	     workflow => {
			  actor => $workflow_output_selector,
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

    my $document_output_available;

    my $output_available_unique
	= {
	  };

    my $render = 1;

    foreach my $column (qw(
			   0
			   1
			  ))
    {
	my $document_name = 'output-selector';

	my $name = "field_${document_name}_configuration_content_$column";

	my $value = $query->param($name);

	if (!defined $value)
	{
	    $render = 0;

	    last;
	}

	if ($value eq 'All')
	{
	    my $target = $uniques->[$column];

	    #! remove 'All' entry

	    $output_available_unique->{$column} = [ (@$target)[1 .. $#$target], ];
	}
	else
	{
	    $output_available_unique->{$column} = [ $value, ];
	}
    }

    print STDERR "output_available_unique is\n" . Dumper($output_available_unique);

    if ($render)
    {
	my $output_available
	    = {
	       map
	       {
		   my $row = $_;

		   my %result
		       = (
			  $row => {
				   map
				   {
				       $_ => 0,
				   }
				   @{$output_available_unique->{1}},
				  },
			 );

		   %result;
	       }
	       @{$output_available_unique->{0}},
	      };

	print STDERR "output_available is\n" . Dumper($output_available);

	my $format_output_available
	    = {
	       columns => [
			   {
			    be_defined => 1,
			    header => 'Model Name',
			    key_name => undef,
			    type => 'constant',
			   },
			   map
			   {
			       my $column_label = $output_available_unique->{1}->[$_ - 1];

			       my $result
				   = {
				      alignment => 'left',
				      be_defined => 1,
				      generate =>
				      sub
				      {
					  my $self = shift;

					  my $row_key = shift;

					  my $row = shift;

					  my $filter_data = shift;

					  my $result = '';

					  #t this can give conflicts

					  my $schedule_header;

					  if ($column_label =~ /FREQ/)
					  {
					      $schedule_header = "conceptual_parameters_$column_label";
					  }
					  else
					  {
					      $schedule_header = "current_$column_label";
					  }

					  my $schedule_exists = -r "$ssp_directory/schedules/generated__${row_key}__${schedule_header}.yml";

					  if ($schedule_exists)
					  {
					      $result .= "<a href=\"/neurospaces_simulation_browser/?project_name=${project_name}&subproject_name=${subproject_name}&module_name=${module_name}&schedule_name=${row_key}__${schedule_header}\"><font size=\"-2\" style=\"position: left: 20%;\"> SSP </font></a> &nbsp;&nbsp;&nbsp;";

					      $result .= "<a href=\"/neurospaces_simulation_browser/?project_name=${project_name}&subproject_name=${subproject_name}&module_name=${module_name}&schedule_name=${row_key}__${schedule_header}&action_name=model\"><font size=\"-2\" style=\"position: left: 20%;\"> Model </font></a> &nbsp;&nbsp;&nbsp;";
					  }
					  else
					  {
					      $result .= "<font size=\"-2\" style=\"position: left: 20%;\"> No SSP </font>";
					  }

					  my $output_exists = -r "$ssp_directory/output/generated__${row_key}__${schedule_header}";

					  if ($output_exists)
					  {
					      $result .= "<a href=\"/neurospaces_output_browser/output.cgi?project_name=${project_name}&subproject_name=${subproject_name}&module_name=${module_name}&schedule_name=${row_key}__${schedule_header}\"><font size=\"-2\" style=\"position: left: 20%;\"> Outputs </font></a> &nbsp;&nbsp;&nbsp;";
					  }
					  else
					  {
					      $result .= "<font size=\"-2\" style=\"position: left: 20%;\"> No output </font>";
					  }

					  if ($editable
					      && $output_exists)
					  {
					      $result
						  .= $self->_encapsulate_checkbox
						      (
						       $self->{name} . $self->{separator} . $column_label . $self->{separator} . $row_key,
						       $_,
						       $output_available->{$row_key}->{$column_label},
						       {},
						      );

					  }
					  else
					  {
					      $result .= '&nbsp;';
					  }
				      },
				      header => $column_label,
				      key_name => $column_label,
				      type => 'code',
				     };

			       $result;
			   }
			   1 .. @{$output_available_unique->{1}},
			  ],
	       hashkey => 'Model Name',
	      };

	$document_output_available
	    = Sesa::TableDocument->new
		(
		 CGI => $query,
		 center => 1,
		 column_headers => 1,
		 contents => $output_available,
		 format => $format_output_available,
		 has_submit => $editable,
		 has_reset => $editable,
		 header => 'Raw Simulation Output
<h4> Select the simulations you are interested in, then submit.
<br> You can inspect individual simulation parameters and raw output by clicking the hyperlinks.
<br> Tip: click the middle mouse button to open the parameters or outputs in a new tab. </h4>',
		 hidden => {
			    session_id => $session_id_digest,
			    $project_name ? ( project_name => $project_name, ) : (),
			    $subproject_name ? ( subproject_name => $subproject_name, ) : (),
			    $module_name ? ( module_name => $module_name, ) : (),
			   },
		 name => 'output-available',
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
		 sort => sub { return $_[0] cmp $_[1]; },
		 # 	     submit_actions => {
		 # 				'output-selector' =>
		 # 				sub
		 # 				{
		 # 				    my ($document, $request, $contents, ) = @_;

		 # 				    # merge the new data into the old data

		 # 				    map
		 # 				    {
		 # 					$column_specification->{$_}->{outputs}
		 # 					    = $contents->{$_}->{value};
		 # 				    }
		 # 					keys %$column_specification;

		 # 				    # write the new content

		 # 				    specification_write($module_name, $scheduler, [ $submitted_request ] );

		 # 				    return $contents;
		 # 				},
		 # 			       },
		 workflow => {
			      actor => $workflow_output_selector,
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

	my $a;

    }

    return [ $document_output_selector, (defined $document_output_available ? ($document_output_available) : ()), ];
}


sub formalize_output_root
{
    my $documents = shift;

    documents_formalize($documents, { rulers => 1, }, );
}


sub main
{
    if (!-r $ssp_directory
        || !-r "$ssp_directory")
    {
	&header('Simulation Output Browser', "", undef, 1, 1, '', '', '');

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
	&header("Simulation Output Browser", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	my $documents = document_output_root($ssp_directory);

	my $data = documents_parse_input($documents);

	documents_merge_data($documents, $data);

	formalize_output_root($documents);

	# finalize (web|user)min specific stuff.

	&footer("index.cgi", 'Simulation Output Browser');
    }
}


main();


