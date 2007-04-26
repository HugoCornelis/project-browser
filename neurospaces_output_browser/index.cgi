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

    print STDERR "uniques is:\n" . Dumper($uniques);

    my $format_outputs
	= {
	   columns =>
	   [
	    {
	     header => 'Model Name',
	     key_name => 'label',
	     type => 'constant',
	     be_defined => 1,
	    },
	    {
	     header => 'Protocol',
	     key_name => 'value',
	     type => 'constant',
	     be_defined => 1,
	    },
	   ],
	  };

    my $document_outputs
	= Sesa::TableDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     column_headers => 1,
	     contents => $uniques,
	     format => $format_outputs,
	     has_submit => $editable == 2,
	     has_reset => $editable == 2,
	     header => 'Outputs Selections',
# 	     hidden => {
# 			$module_name ? ( module_name => $module_name, ) : (),
# 			$submodule_name ? ( submodule_name => $submodule_name, ) : (),
# 		       },
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
	     row_filter => sub { !ref $_[1]->{value}, },
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
# 	     workflow => {
# 			  actor => $workflow_outputs,
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

    return [ $document_outputs, ];
}


sub formalize_output_root
{
    my $documents = shift;

    documents_formalize($documents, { rulers => 1, }, );
}


sub main
{
    $query = CGI->new(<STDIN>);

    if (!-r $ssp_directory
        || !-r "$ssp_directory/output")
    {
	&header('Simulation Browser and Editor', "", undef, 1, 1, '', '', '');

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
	my $module_name = $query->param('module_name');

	if (!defined $module_name)
	{
	    my $submodules = do './submodules.pl';

	    &header("SSP Simulation Browser", "", undef, 1, 1, 0, '');

	    print "<hr>\n";

	    my $documents = document_output_root($ssp_directory);

	    my $data = documents_parse_input($documents);

	    documents_merge_data($documents, $data);

	    formalize_output_root($documents);

	    # finalize (web|user)min specific stuff.

	    &footer("index.cgi", 'SSP Simulation Browser');
	}
	else
	{
	    my $submodule_name = $query->param('submodule_name');

	    if (!defined $submodule_name || $submodule_name eq '')
	    {
		&header("SSP Schedule: $module_name", "", undef, 1, 1, '', '', '');

		print "<hr>\n";

		use YAML;

		my $filename = "generated__$module_name.yml";

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

		my $documents = document_ssp_schedule($scheduler, $module_name, );

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

		my ($sesa_specification, $read_error) = specification_read($module_name);

		if ($read_error)
		{
		    &error($read_error);
		}

		my $documents = document_ssp_schedule($sesa_specification, $module_name, $submodule_name, );

		my $data = documents_parse_input($documents);

		documents_merge_data($documents, $data);

		formalize_sesa_outputs_for_module($documents);

		# finalize (web|user)min specific stuff.

		&footer("index.cgi", 'Persistency Layer Editors', "outputs.cgi", 'Output Editor', "outputs.cgi?module_name=${module_name}", ${module_name});
	    }
	}
    }
}


main();


