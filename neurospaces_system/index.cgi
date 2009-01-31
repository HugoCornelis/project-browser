#!/usr/bin/perl -d:ptkdb -w
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
						     label => 'administration of projects',
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


my $all_projects;

sub document_projects
{
    # load module specifics

    use YAML 'LoadFile';

    my $module_description;

    my $module_configuration;

    my $header = $module_configuration->{description} || 'Project Administration';

    print STDERR "header is $header\n";

    print "<center><h3>$header</h3></center>\n";

    print "<hr>" ;

    # check if a module command was called

    # get all information from the database

    use Neurospaces::Project 'projects_read';

    my $all_projects = projects_read();

    my $format_projects
	= {
	   columns =>
	   [
	    {
	     be_defined => 1,
	     header => 'Project ID',
	     key_name => 'dummy1',
	     type => 'constant',
	    },
	    {
	     filter_defined => 1,
	     encapsulator => {
			      options => {
					  -maxlength => 30,
					  -size => 35,
					 },
			     },
	     header => 'Name',
	     key_name => 'name',
	     type => 'textfield',
	    },
	    {
	     filter_defined => 1,
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
	     filter_defined => 1,
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
			   -href => "?morphology_group_name=${row_key}&operation_name=view",
			  },
			  "View",
			 );

		 return($result);
	     },
	     header => 'View',
	     key_name => 'view',
	     type => 'code',
	    },
	    {
	     filter_defined => 1,
	     generate =>
	     sub
	     {
		 print STDERR "generate:\n", Dumper(\@_);

		 my $self = shift;

		 my $group_name = shift;

		 my $group = shift;

		 my $filter_data = shift;

		 if ($editable)
		 {
		     return
			 $query->submit
			     (
			      -name  => "button_$self->{name}_something",
			      -value => ' Delete ',
			      (!1 ? (-disabled => 1) : ()),
			     );
		 }
		 else
		 {
		     return "&nbsp;";
		 }
	     },
	     header => 'Add / Delete',
	     key_name => 'add_delete',
	     type => 'code',
	    },
	   ],
	   hashkey => 'Project ID',
	  };

    my $session_id_digest = $query->param('session_id');

    if (!defined $session_id_digest)
    {
	my $session_id = rand(10000);

	use Digest::SHA1 'sha1_base64';

	$session_id_digest = sha1_base64($session_id);
    }

    my $workflow_projects
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

    my $document_projects
	= Sesa::TableDocument->new
	    (
	     CGI => $query,
	     center => 1,
	     column_headers => 1,
	     contents => $all_projects->{projects},
	     format => $format_projects,
	     has_submit => $editable,
	     has_reset => $editable,
	     header => '<h2> All Projects </h2>
<h4> Project Administration </h4>
<h5> Change Project Descriptions, Create New Projects, Delete Existing Projects. </h5>',
	     hidden => {
			session_id => $session_id_digest,
		       },
	     name => 'all-projects',
	     output_mode => 'html',
	     regex_encapsulators => [
				     {
				      match_content => 1,
				      name => 'channel-inhibited-editfield-encapsulator',
				      regex => ".*NEW_.*",
				      type => 'constant',
				     },
				    ],
 	     row_filter =>
	     sub
	     {
# 		 my $row_key = shift;

# 		 my $row = shift;

		 # add the analyze key to generate the hyperlinks

		 return
		 {
# 		  number_of_cells => (scalar grep { $_[1]->{morphologies}->{$_} } keys %{$_[1]->{morphologies}}),
		  description => $_[1]->{description} || '',
		  name => $_[1]->{name} || '',
		  add_delete => 1,
		  view => 1,
		  %{$_[1]},
		 };
	     },
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
		     $result .= $query->textfield(
						  -name      => "field$self->{separator}$self->{name}_add_group-description",
						  -default   => '',
						  -override  => 1,
						  -size      => 35,
						  -maxlength => 30,
						 );
		     $result .= "</td>";

		     $result .= "<td style='border-left-style: hidden'></td>";

		     {
			 $result .= "<td align='center'>";

			 $result .= "&nbsp;--&nbsp;";

			 $result .= "</td>";

			 $result .= "<td style='border-left-style: hidden'></td>";
		     }

		     $result .= "<td align='center'>";

		     $result
			 .= $query->submit(
					   -name  => "button_$self->{name}_add",
					   -value => ' Add ',
					  );
		     $result .= "</td>";

		     $result .= "<td style='border-left-style: hidden'></td>";

		 }

		 return($result);
	     },
	     separator => '/',
	     sort => sub { return $_[2]->{number} <=> $_[3]->{number} },
	     button_actions => {
				add =>
				sub
				{
				    my ($document, $request, $contents, ) = @_;

				    my $action = $request;

				    #t get other data
				},
			       },
	     submit_actions => {
				'all-projects' =>
				sub
				{
				    my ($document, $request, $contents, ) = @_;

				    use YAML 'LoadFile';

# 				    # merge the new data into the old data

# 				    map
# 				    {
# 					$column_specification->{$_}->{outputs}
# 					    = $contents->{$_}->{value};
# 				    }
# 					keys %$column_specification;

# 				    # write the new content

# 				    specification_write($module_name, $scheduler, [ $submitted_request ] );

				    return $contents;
				},
			       },
	     workflow => {
			  actor => $workflow_projects,
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

    return [ $document_projects, ];

#     print "<hr>" ;

}


sub formalize_projects
{
    my $documents = shift;

    documents_formalize($documents, { rulers => 1, }, );
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
    else
    {
	&header("Project Browser", "", undef, 1, 1, 0, '');

	print "<hr>\n";

	my $documents = document_projects();

	my $data = documents_parse_input($documents);

	documents_merge_data($documents, $data);

	formalize_projects($documents);

	# finalize (web|user)min specific stuff.

	&footer("/", $::text{'index'}, "/neurospaces_project_browser/", 'All Projects');
    }
}


main();


