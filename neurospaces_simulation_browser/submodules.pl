#!/usr/bin/perl -w
#

my $neurospaces_config = do '/etc/neurospaces/neurospaces.config';

my $project_name = $query->param('project_name');

my $subproject_name = $query->param('subproject_name');

my $module_name = $query->param('module_name');

my $ssp_directory = $neurospaces_config->{simulation_browser}->{root_directory} . "$project_name/$subproject_name/$module_name";


my $ssp_schedules = [ grep { /^\w+$/ } map { chomp; $_; } `/bin/ls -1 "$ssp_directory/"`, ];


my $submodules
    = {
       map
       {
	   use YAML;

	   my $schedule = $_;

	   my $scheduler;

	   eval
	   {
	       local $/;

	       $scheduler = Load(`cat "$filename"`);
	   };

	   if ($@)
	   {
	       print "$0: scheduler cannot be constructed from '$filename': $@, ignoring this schedule\n";

	       die "$0: scheduler cannot be constructed from '$filename': $@, ignoring this schedule";
	   }

	   ( $schedule => $scheduler->{name}, );
       }
       $@ssp_schedules,
      };

return $submodules;

