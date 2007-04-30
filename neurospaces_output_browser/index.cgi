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


my $query;


my $ssp_directory = '/local_home/local_home/hugo/neurospaces_project/purkinje-comparison';


sub document_output_root
{
    my $ssp_directory = shift;

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
# 			$module_name ? ( module_name => $module_name, ) : (),
# 			$submodule_name ? ( submodule_name => $submodule_name, ) : (),
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
					      $result .= "<a href=\"/neurospaces_simulation_browser/?schedule_name=${row_key}__${schedule_header}\"><font size=\"-2\" style=\"position: left: 20%;\"> SSP </font></a> &nbsp;&nbsp;&nbsp;";
					  }
					  else
					  {
					      $result .= "<font size=\"-2\" style=\"position: left: 20%;\"> No SSP </font>";
					  }

					  my $output_exists = -r "$ssp_directory/output/generated__${row_key}__${schedule_header}";

					  if ($output_exists)
					  {
					      $result .= "<a href=\"/neurospaces_simulation_browser/?schedule_name=${row_key}__${schedule_header}\"><font size=\"-2\" style=\"position: left: 20%;\"> Outputs </font></a> &nbsp;&nbsp;&nbsp;";
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
		 header => 'Simulation Selections
<h4> Select the simulations you are interested in, then submit.
<br> You can inspect individual simulation parameters and output by clicking the hyperlinks.
<br> Tip: click the middle mouse button to open the parameters or outputs in a new tab. </h4>',
		 hidden => {
			    session_id => $session_id_digest,
			    # 			$module_name ? ( module_name => $module_name, ) : (),
			    # 			$submodule_name ? ( submodule_name => $submodule_name, ) : (),
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
    $query = CGI->new();

    if (!-r $ssp_directory
        || !-r "$ssp_directory/output")
    {
	&header('Simulation Output Browser', "", undef, 1, 1, '', '', '');

	print "<hr>\n";

	print "<center>\n";

	print "<H3>The simulation directory does not exist.</H3>";

	print "<p>\n";

	print "$ssp_directory/output not found\n";

	print "</center>\n";

	print "<hr>\n";

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'});
    }
    else
    {
	my $schedule_name = $query->param('schedule_name');

	if (!defined $schedule_name)
	{
	    my $submodules = do './submodules.pl';

	    &header("Simulation Output Browser", "", undef, 1, 1, 0, '');

	    print "<hr>\n";

	    my $documents = document_output_root($ssp_directory);

	    my $data = documents_parse_input($documents);

	    documents_merge_data($documents, $data);

	    formalize_output_root($documents);

	    # finalize (web|user)min specific stuff.

	    &footer("index.cgi", 'Simulation Output Browser');
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

		    $scheduler = Load(`cat "$ssp_directory/output/$filename"`);
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

		formalize_sesa_outputs_for_module($documents);

		# finalize (web|user)min specific stuff.

		&footer("index.cgi", 'Output Browser');
	    }
	    else
	    {
		&header("Output Editor", "", undef, 1, 1, '', '', '');

		print "<hr>\n";

		my ($sesa_specification, $read_error) = specification_read($schedule_name);

		if ($read_error)
		{
		    &error($read_error);
		}

		my $documents = document_ssp_schedule($sesa_specification, $schedule_name, $subschedule_name, );

		my $data = documents_parse_input($documents);

		documents_merge_data($documents, $data);

		formalize_sesa_outputs_for_module($documents);

		# finalize (web|user)min specific stuff.

		&footer("index.cgi", 'Persistency Layer Editors', "outputs.cgi", 'Output Editor', "outputs.cgi?schedule_name=${schedule_name}", ${schedule_name});
	    }
	}
    }
}


main();


