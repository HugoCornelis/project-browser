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
use Sesa::TableDocument;
use Sesa::Transform;
use Sesa::TreeDocument;
use Sesa::Workflow;


my $query;


my $neurospaces_config = do '/var/neurospaces/neurospaces.config';

my $ssp_directory = $neurospaces_config->{simulation_browser}->{root_directory} . "purkinje-comparison/modules/1";


sub document_ssp_outputs
{
    my $outputs = shift;

    my $schedule_name = shift;

    my $format_output_selector
	= {
	   columns =>
	   [
	    {
	     header => 'Output Label',
	     key_name => 'a',
	     type => 'constant',
	     filter_defined => 1,
	    },
	    {
	     header => 'Actions',
	     key_name => 'b',
	     type => 'code',
	     filter_defined => 1,
	     generate =>
	     sub
	     {
		 my $self = shift;

		 my $row_key = shift;

		 my $row = shift;

		 my $filter_data = shift;

		 my $result = '';

		 $result .= "<a href=\"/neurospaces_output_browser/output.cgi?schedule_name=${schedule_name}&output_name=$row\"><font size=\"-2\" style=\"position: left: 20%;\"> plot </font></a> &nbsp;&nbsp;&nbsp;";
	     },
	    },
	    {
	     header => 'Selection',
	     key_name => 'c',
	     type => 'checkbox',
	     filter_defined => 1,
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
			  {
			   label => "Simulation Schedule",
			   target => "/neurospaces_simulation_browser/?schedule_name=$schedule_name",
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
	     contents => $outputs,
	     format => $format_output_selector,
	     has_submit => $editable,
	     has_reset => $editable,
	     header => 'Output Selections
<h4> Select fields of interest, then submit.
<br> You can inspect individual outputs by clicking the hyperlinks.
</h4>
',
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
	     row_filter => sub { { a => $_[1], b => '', c => 0, }; },
	     separator => '/',
	     sort => sub { return $_[0] <=> $_[1] },
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

    my $render = 0;

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
					      $result .= "<a href=\"/neurospaces_output_browser/?schedule_name=${row_key}__${schedule_header}\"><font size=\"-2\" style=\"position: left: 20%;\"> Outputs </font></a> &nbsp;&nbsp;&nbsp;";
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
    }

    return [ $document_output_selector, (defined $document_output_available ? ($document_output_available) : ()), ];
}


sub formalize_ssp_outputs
{
    my $documents = shift;

    documents_formalize($documents, { rulers => 1, }, );
}


sub main
{
    $query = CGI->new();

    use YAML;

    my $schedule_name = $query->param('schedule_name');

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

    my $transformator
	= Sesa::Transform->new
	    (
	     contents => $scheduler,
	     name => 'simulation-output-extractor',
	     transformators =>
	     [
	      sub
	      {
		  my ($transform_data, $context, $contents) = @_;

		  # 			  my $top = Sesa::Transform::_context_get_current($context);
		  # $top->{type} eq 'SCALAR'
		  if ($context->{path} =~ m|^[^/]*/outputs/([^/]*)$|)
		  {
		      my $content = Sesa::Transform::_context_get_current_content($context);

		      my $result = Sesa::Transform::_context_get_main_result($context);

		      if (!$result->{content}->{outputs})
		      {
			  $result->{content}->{outputs} = [];
		      }

		      push
			  @{$result->{content}->{outputs}},
			  {
			   component_name => $content->{component_name},
			   field => $content->{field},
			  };

		      return;
		  }
	      },
	     ],
	    );

    my $concatenator
	= Sesa::Transform->new
	    (
	     name => 'simulation-output-concatenator',
	     source => $transformator,
	     transformators =>
	     [
	      sub
	      {
		  my ($transform_data, $context, $contents) = @_;

		  if ($context->{path} =~ m|^[^/]*/outputs/([^/]*)$|)
		  {
		      my $content = Sesa::Transform::_context_get_current_content($context);

		      my $result = Sesa::Transform::_context_get_main_result($context);

		      if (!$result->{content}->{outputs})
		      {
			  $result->{content}->{outputs} = [];
		      }

		      push
			  @{$result->{content}->{outputs}},
			      $content->{component_name} . '->' . $content->{field};

		      return;
		  }
	      },
	     ],
	    );

    my $count = 0;

    my $array_to_hasher
	= Sesa::Transform->new
	    (
	     name => 'array_to_hasher',
	     # 		     separator => '!',
	     source => $concatenator,
	     transformators =>
	     [
# 	      Sesa::Transform::_lib_transform_array_to_hash('outputs', '->{outputs}'),
	      sub
	      {
		  my ($transform_data, $context, $contents) = @_;

		  if ($context->{path} =~ m|^[^/]*/outputs/([^/]*)$|)
		  {
		      my $content = Sesa::Transform::_context_get_current_content($context);

		      my $result = Sesa::Transform::_context_get_main_result($context);

		      $result->{content}->{$count} = $content;

		      $count++;

		      return;
		  }
	      },
	     ],
	    );

    my $outputs = $array_to_hasher->transform();

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
	my $output_name = $query->param('output_name');

	if (!defined $output_name || $output_name eq '')
	{
	    &header("SSP Schedule: $schedule_name", "", undef, 1, 1, '', '', '');

	    print "<hr>\n";

	    my $documents = document_ssp_outputs($outputs, $schedule_name, );

	    my $data = documents_parse_input($documents);

	    documents_merge_data($documents, $data);

	    formalize_ssp_outputs($documents);

	    # finalize (web|user)min specific stuff.

	    &footer("index.cgi", 'Output Browser');
	}
	else
	{
	    use File::Temp qw/ :mktemp /;

	    use Math::Trig qw [pi];

	    use PDL;
	    use PDL::Graphics::PLplot;

	    # get a temporary file

	    #t note that this is an unsafe implementation

	    my $filename_pbm = mktemp("../tmp/neurospaces_output_pbm_XXXXXXXXXXXX");

	    #! needed for mime types below, here needed for consistency

	    $filename_pbm .= ".pbm";

	    # determine the column to extract from the output file

	    my $column_extractor = { reverse %$outputs, };

	    #! + 1 for time step

	    my $column = $column_extractor->{$output_name} + 1;

	    # create plot object

	    $output_name =~ /->(.*)$/;

	    my $units
		= {
		   'Ca' => 'mol',
		   'Gk' => 'Siemens',
		   'Ik' => 'Current',
		   'Vm' => 'Vm',
		   'state_x' => 'prob.',
		   'state_y' => 'prob.',
		  };

	    my $unit = $units->{$1} || 'Y';

	    my $pl
		= PDL::Graphics::PLplot->new
		    (
		     DEV => "pbm",
		     FILE => $filename_pbm,
		     PAGESIZE => [ 1000, 900, ],
		     XLAB => 'Time (s)',
		     YLAB => $unit,
		    );

	    #! + 1 for time step

	    my $columns = [ 0 .. (keys %$outputs) + 1, ];

	    my $output_filename = $ssp_directory . "/output/generated__" . $schedule_name;

	    @$columns = PDL->rcols($output_filename, 0, $column);

	    # add the extracted columns to the plot

	    $pl->xyplot($columns->[0], $columns->[1]); # $columns->[$column]);

	    $pl->close();

	    my $filename_png = mktemp("../tmp/neurospaces_output_png_XXXXXXXXXXXX");

	    $filename_png .= ".png";

	    system "convert \"$filename_pbm\" \"$filename_png\"";

	    if ($?)
	    {
		print STDERR "system operator error: $?\n";
	    }

	    &header("Output Plotter: $output_name (column $column)", "", undef, 1, 1, '', '', '');

	    print "<hr>\n";

# 	    my $documents = document_ssp_schedule($sesa_specification, $schedule_name, $output_name, );

# 	    my $data = documents_parse_input($documents);

# 	    documents_merge_data($documents, $data);

# 	    formalize_sesa_outputs_for_module($documents);

	    print "<center>\n";

	    print "<img src=\"$filename_png\" alt=\"a plplot image\" border=0>\n";

	    print "</center>\n";

	    print "<hr>\n";

	    # finalize (web|user)min specific stuff.

	    &footer("index.cgi", 'Persistency Layer Editors', "outputs.cgi", 'Output Editor', "outputs.cgi?schedule_name=${schedule_name}", ${schedule_name});
	}
    }
}


main();


