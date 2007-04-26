#!/usr/bin/perl -d:ptkdb -w
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

    my $format_outputs
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
		     return "&nbsp;";
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
		     return "&nbsp;";
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

    my $document_output_selector
	= Sesa::TableDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     column_headers => 1,
	     contents => { content => $uniques, },
	     format => $format_outputs,
	     has_submit => $editable,
	     has_reset => $editable,
	     header => 'Output Selections
<h3> Select a model and protocol, then submit </h3>',
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

    return [ $document_output_selector, ];
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


