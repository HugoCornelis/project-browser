# $Id: submodules.pl,v 1.3 2005/06/13 15:41:03 hco Exp $

my $ssp_directory = '/local_home/local_home/hugo/neurospaces_project/purkinje-comparison';


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

