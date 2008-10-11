#!/usr/bin/perl -w
#!/usr/bin/perl -d:ptkdb -w
#
# (C) 2007 Hugo Cornelis hugo.cornelis@gmail.com
#


package Neurospaces::Project::Modules::Morphology;


use strict;


require Exporter;

our @ISA = qw(Exporter);

our @EXPORT_OK
    = qw(
	 morphologies_read
	 morphologies_write
	 morphology_groups_read
	 morphology_groups_write
	);


sub morphologies_read
{
    my $project = shift;

    my $project_name = $project->{name};

    my $project_root = $project->{root};

    #t replace with File::Find;

    my $result = [ sort map { chomp; $_; } `find "$project_root/$project_name/morphologies" -name "*.ndf" -o -name "*.p" -o -iname "*.swc"`, ];

    return $result;
}


sub morphologies_write
{
    die "morphologies_write() is not implemented";
}


sub morphology_groups_read
{
    my $project = shift;

    my $project_name = $project->{name};

    my $project_root = $project->{root};

    use YAML 'LoadFile';

    my $result;

    eval
    {
	$result = LoadFile("$project_root/$project_name/morphology_groups/descriptor.yml");
    };

    return $result;
}


sub morphology_groups_validate
{
    my $project = shift;

    my $morphology_groups = shift;

    my $result;

    #t do validation

    $result = '';

    return $result;
}


sub morphology_groups_write
{
    my $project = shift;

    my $project_name = $project->{name};

    my $project_root = $project->{root};

    my $morphology_groups = shift;

#     use YAML 'DumpFile';

    my $result;

    $result = morphology_groups_validate($project, $morphology_groups);

    if ($result)
    {
	return $result;
    }

    use Sesa::Persistency;

    Sesa::Persistency::create_backup_and_write("$project_root/$project_name/morphology_groups/descriptor.yml", $morphology_groups);

#     #t should use Sesa backup mechanism overhere

#     eval
#     {
# 	DumpFile("$project_root/$project_name/morphology_groups/descriptor.yml", $morphology_groups);
#     };

    return $result;
}


1;


