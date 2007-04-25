#!/usr/bin/perl -w
#
# $Id: Webmin.pm,v 1.1 2005/02/09 09:28:47 hco Exp $
#

#
# Interface between Webmin and Sesa, mainly implemented by
# copy-pasting code from Webmin's libraries, and making them modular
# such that they can be reused by external modules.
#

package Sesa::Webmin;


our @EXPORT_OK = qw(
		    restart_miniserv
		   );


#t Webmin::File abstraction.
#t
#t ->read()
#t ->write()
#t

#t Webmin::Process abstraction.
#t
#t ->restart()
#t ->configure()
#t

# restart_miniserv()
# Kill the old miniserv process and re-start it
sub restart_miniserv
{
    my ($pid, %miniserv);

#     &get_miniserv_config(\%miniserv) || return;
#     $miniserv{'inetd'} && return;

    open(PID, "/var/webmin/miniserv.pid")
	|| &error("Failed to open pid file");

    chop($pid = <PID>);

    close(PID);

    if (!$pid)
    {
	&error("Invalid pid file");
    }

    # Just signal miniserv to restart

    kill_logged('HUP', $pid);
}

# kill_logged(signal, pid, ...)
sub kill_logged
{
#     &additional_log('kill', $_[0], join(" ", @_[1..@_-1])) if (@_ > 1);

    return kill(@_);
}

