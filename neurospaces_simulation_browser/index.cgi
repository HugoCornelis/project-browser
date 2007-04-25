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


my $query;


my $ssp_directory = '/local_home/local_home/hugo/neurospaces_project/purkinje-comparison/schedules';


sub document_ssp_schedule
{
    my $scheduler = shift;

    my $module_name = shift;

    my $submodule_name = shift || '';

    my $column_specification;

    my $submitted_request;

#     if (exists $sesa_specification->{column_specifications}->{$submodule_name}->{column_specification})
#     {
# 	$column_specification = $sesa_specification->{column_specifications}->{$submodule_name}->{column_specification};

# 	$submitted_request = "column_specification_$submodule_name";
#     }
#     else
#     {
# 	$column_specification = $sesa_specification->{column_specification};

# 	$submitted_request = 'column-specification';
#     }

#     my $units
# 	= {
# 	   map
# 	   {
# 	       $_ => {
# 		      label => $column_specification->{$_}->{description},
# 		      name => $_,
# 		      value => $column_specification->{$_}->{units} || '',
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

#     my $format_units
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

    my $header = "SSP Schedule $module_name";

#     if ($submodule_name)
#     {
# 	$header .= ", Submodule $submodule_name";
#     }

#     my $workflow_units
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
# 			    target => "/sems_sesa_persistency_editor/units.cgi?module_name=$module_name",
# 			   },
# 			  ],
# 	      related => [
# 			  {
# 			   label => "Run module $module_name",
# 			   target => '/' . specification_get_module_directory( { module => [ $module_name, ], }, ),
# 			  },
# 			  {
# 			   label => 'Defaults',
# 			   target => "/sems_sesa_persistency_editor/defaults.cgi?module_name=$module_name&submodule_name=$submodule_name",
# 			  },
# 			  {
# 			   label => 'Labels',
# 			   target => "/sems_sesa_persistency_editor/labels.cgi?module_name=$module_name&submodule_name=$submodule_name",
# 			  },
# 			  {
# 			   label => 'Row Order',
# 			   target => "/sems_sesa_persistency_editor/order.cgi?module_name=$module_name&submodule_name=$submodule_name",
# 			  },
# 			  {
# 			   label => 'Headers',
# 			   target => "/sems_sesa_persistency_editor/heditor.cgi?module_name=$module_name&submodule_name=$submodule_name",
# 			  },
# 			 ],
# 	     },
# 	     {
# 	      self => $ENV{REQUEST_URI},
# 	     },
# 	    );

    my $document_units
	= Sesa::TreeDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     column_headers => 1,
	     contents => $scheduler,
# 	     format => $format_units,
	     has_submit => $editable == 2,
	     has_reset => $editable == 2,
	     header => $header,
	     hidden => {
			$module_name ? ( module_name => $module_name, ) : (),
			$submodule_name ? ( submodule_name => $submodule_name, ) : (),
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
# 					$column_specification->{$_}->{units}
# 					    = $contents->{$_}->{value};
# 				    }
# 					keys %$column_specification;

# 				    # write the new content

# 				    specification_write($module_name, $scheduler, [ $submitted_request ] );

# 				    return $contents;
# 				},
# 			       },
# 	     workflow => {
# # 			  actor => $workflow_units,
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

    return [ $document_units, ];
}


sub formalize_sesa_units_for_module
{
    my $documents = shift;

    documents_formalize($documents, { rulers => 1, }, );
}


sub formalize_ssp_root
{
    my $ssp_directory = shift;

    # get all information from the database

    my $unit_modules = [ sort map { s/^generated__//; s/\.yml$//; $_; } grep { /^generated__/ } map { chomp; $_; } `/bin/ls -1 "$ssp_directory/"`, ];

    my @links;
    my @titles;
    my @icons;

    foreach my $module (@$unit_modules)
    {
	#    if ($access{$submodule})
	{
	    push(@links, "?module_name=${module}");
	    push(@titles, $module);

	    my $icon = 'images/ssp32x32.png';

	    push(@icons, $icon, );
	}
    }

    &icons_table(\@links, \@titles, \@icons);

    print "<hr>" ;

}


sub main
{
    $query = CGI->new(<STDIN>);

    if (!-r $ssp_directory)
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
    else
    {
	my $module_name = $query->param('module_name');

	if (!defined $module_name)
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

		    $scheduler = Load(`cat "$ssp_directory/$filename"`);
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

		formalize_sesa_units_for_module($documents);

		# finalize (web|user)min specific stuff.

		&footer("index.cgi", 'SSP Simulation Browser');
	    }
	    else
	    {
		&header("Unit Editor", "", undef, 1, 1, '', '', '');

		print "<hr>\n";

		my ($sesa_specification, $read_error) = specification_read($module_name);

		if ($read_error)
		{
		    &error($read_error);
		}

		my $documents = document_ssp_schedule($sesa_specification, $module_name, $submodule_name, );

		my $data = documents_parse_input($documents);

		documents_merge_data($documents, $data);

		formalize_sesa_units_for_module($documents);

		# finalize (web|user)min specific stuff.

		&footer("index.cgi", 'Persistency Layer Editors', "units.cgi", 'Unit Editor', "units.cgi?module_name=${module_name}", ${module_name});
	    }
	}
    }
}


main();


