#!/usr/bin/perl -w
#

my $neurospaces_config = do '/var/neurospaces/neurospaces.config';

my $ssp_directory = $neurospaces_config->{simulation_browser}->{root_directory} . "purkinje-comparison/modules/1";


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

