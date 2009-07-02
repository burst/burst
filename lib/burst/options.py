"""
Command line and default config file for BURST robocup platform.
"""

import os
from burst_consts import (ROBOT_IP_TO_NAME, BLUE_TEAM, RED_TEAM)
import burst_consts

__all__ = ['running_on_nao', 'connecting_to_webots', 'connecting_to_nao',
    'options', 'ip', 'port', 'set_all_verbose']

try: # doesn't work on opennao
    from socket import getaddrinfo # for resolving a hostname
except:
    getaddrinfo = lambda ip, port: [[None, None, None, None, [ip]]]
    print "WARNING: socket is missing. Did you follow https://shwarma.cs.biu.ac.il/moin/InstallingNaoMan?"

def running_on_nao():
    """ True if we are physically on the nao geode brain box """
    return os.path.exists('/opt/naoqi/bin/naoqi')

def connecting_to_webots():
    """ True if we are connecting to webots """
    #is_nao = os.popen("uname -m").read().strip() == 'i586'
    return not running_on_nao() and ip == LOCALHOST_IP or ip == 'localhost'

def connecting_to_nao():
    """ True if we are not connecting to webots.
    Note that this doesn't imply running_on_nao, since we can
    be connecting remotely """
    return not connecting_to_webots()


def parse_command_line_arguments():
    import sys
    if not hasattr(sys, 'argv'): # fix for bug when importing from within nao-man
        sys.argv=['fake']
    from optparse import OptionParser, OptionGroup
    parser = OptionParser()
    main = OptionGroup(parser, "main")

    main.add_option('', '--daemonize', action='store_true', dest='daemonize', default=False, help='daemonize the process. must be used for competition.')
    main.add_option('', '--ip', dest='ip', help='ip address for broker, default is localhost')
    main.add_option('', '--port', dest='port', help='port used by broker, localhost will default to 9560, rest to 9559')
    main.add_option('', '--jersey', dest='jersey', help='override default per-host-name jersey number in burst_consts')
    main.add_option('', '--color', dest='starting_team_color', default=BLUE_TEAM,
            help='override default start team color - for testing. in game the chest button will be used')
    main.add_option('', '--red', action="store_const", dest="starting_team_color", const=RED_TEAM, help="set starting team color to red")
    main.add_option('', '--blue', action="store_const", dest="starting_team_color", const=BLUE_TEAM, help="set starting team color to blue")
    main.add_option('', '--opposing', dest='opposing', default='yellow', help='override default opposing goal color')
    main.add_option('', '--ticker', action='store_true', dest='ticker', default=False, help='print every dt if there is a change')
    main.add_option('', '--testready', action='store_true', dest='test_ready', default=False, help='test ready state without gamecontroller')
    main.add_option('', '--testconfigure', action='store_true', dest='test_configure', default=False, help='test unconfigured state, disregarding gamecontroller')
    main.add_option('', '--traceproxies', action='store_true', dest='trace_proxies', default=False, help='trace proxy calls')
    main.add_option('', '--console-line-length', action='store', dest='console_line_length', default=burst_consts.CONSOLE_LINE_LENGTH, help='allow for wider/leaner screen debugging')
    main.add_option('', '--passivectrlc', action='store_true', dest='passive_ctrl_c', default=False, help='Don\'t do initPoseAndRelax on Ctrl-C')
    main.add_option('', '--debugpersonal', action='store_true', dest='debug_personal', default=False, help='Remove try around __import__(personal)')
    main.add_option('', '--dt', dest='dt', default=burst_consts.DEFAULT_EVENT_MANAGER_DT, help='main loop time step, in seconds (handle with caution!)')
    # PREGAME TODO: game_controller and game_status should default to TRUE!!
    main.add_option('', '--use_game_controller', action='store_true', dest='game_controller', default=False, help='Use game controller (start in initial state)')
    main.add_option('', '--use_game_status', action='store_true', dest='game_status', default=False, help='Use game controller (start in initial state)')
    main.add_option('', '--runsonar', action='store_true', dest='run_sonar', default=False, help='Run Sonar')

    experimental = OptionGroup(parser, "experimental")
    experimental.add_option('', '--pynaoqi', action='store_true', dest='use_pynaoqi', help='use pynaoqi and twisted (TESTING)')
    experimental.add_option('', '--usepostid', action='store_true', dest='use_postid', default=False, help='affects ThreadedMoveCoordinator only')
    experimental.add_option('', '--newmovecoordinator', action='store_true', dest='new_move_coordinator', default=False, help='debug - use new ThreadedMoveCoordinator')

    debug = OptionGroup(parser, "profile and debug")
    debug.add_option('', '--profile', action='store_true', dest='profile', default=False, help='profile the application')
    debug.add_option('', '--profile-player', action='store_true', dest='profile_player', default=False, help='profile player code')
    debug.add_option('', '--logpositions', action='store_true', dest='log_positions', default=False, help='will record positions of objects into csv files in the current directory, with timestamps')

    # TODO - unsafe isn't required anymore, and also isn't correct for the possible "don't left t.i.d.Deferred's catch our exceptions" scenario.
    debug.add_option('', '--unsafe', action='store_false', dest='catch_player_exceptions', default=True, help='don\'t catch stray exceptions')
    debug.add_option('', '--debug', action='store_true', dest='debug', default=False, help='Turn on debugging code')

    debug.add_option('', '--nomemoryupdates', action='store_true', dest='no_memory_updates', default=False, help='trace proxy calls')

    debug.add_option('', '--verbose-goals', action='store_true', dest='verbose_goals', default=False, help='Verbose objects.Goal, objects.GoalPost')
    debug.add_option('', '--verbose-tracker', action='store_true', dest='verbose_tracker', default=False, help='Verbose tracker/searcher/center')
    debug.add_option('', '--verbose-eventmanager', action='store_true', dest='verbose_eventmanager', default=False, help='Verbose event manager')
    debug.add_option('', '--verbose-localization', action='store_true', dest='verbose_localization', default=False, help='Verbose localization')
    debug.add_option('', '--verbose-journey', action='store_true', dest='verbose_journey', default=False, help='Verbose movecoordinator')
    debug.add_option('', '--verbose-movecoordinator', action='store_true', dest='verbose_movecoordinator', default=False, help='Verbose movecoordinator')
    debug.add_option('', '--verbose-deferreds', action='store_true', dest='verbose_deferreds', default=False, help='Verbose deferreds (burstdeferreds)')
    debug.add_option('', '--verbose-player', action='store_true', dest='verbose_player', default=False, help='Verbose player class')
    debug.add_option('', '--verbose-gamestatus', action='store_true', dest='verbose_gamestatus', default=False, help='Verbose game status class')
    debug.add_option('', '--verbose-reregister', action='store_true', dest='verbose_reregister', default=False, help='Warn on re-register of event callbacks')

    unused = OptionGroup(parser, "unused")
    # old unused
    unused.add_option('', '--bodyposition', dest='bodyposition', help='test app: prints bodyposition continuously')

    pynaoqi = OptionGroup(parser, "pynaoqi")
    true_storers, false_storers, storers = [], [], []

    # Some helper functions for argument parsing
    def collector(opt, col, kw_base, **kw):
        kwjoint = dict(kw_base)
        kwjoint.update(kw)
        pynaoqi.add_option('', opt, **kwjoint)
        col.append(opt)
    store_true =lambda opt, **kw: collector(opt, true_storers, {'action':'store_true', 'default':False}, **kw)
    store_false =lambda opt, **kw: collector(opt, false_storers, {'action':'store_false'}, **kw)
    store = lambda opt, **kw: collector(opt, storers, {'action':'store'}, **kw)

    # Optional Arguments
    #pynaoqi.add_option('', '--video', action='store_true', dest='video', default=False, help='do video')

    store_true('--calibrator', dest='calibrator', default=False,
            help='run calibrator')
    store_true('--video', dest='video', default=False,
            help='run video window')
    store_true('--notes', dest='notes', default=False,
            help='run notes gui')
    store_true('--twisted', dest='twisted', default=True,
            help='use twisted')
    store_true('--multiple', dest='multiple_connections', default=False,
            help='use multiple connections (big memory hog on naoqi process - don\'t use on robot!)')
    store_true('--examples', dest='examples', default=False,
            help='show long examples on start')
    store_false('--notwisted', dest='twisted',
            help='don\'t use twisted')
    store_true('--locon', dest='localization_on_start',
            help='turn localization on')
    store_true('--reportnew', dest='report_new_packet_sizes',
            help='debug - report new packet sizes')
    store_true('--verbosetwisted', dest='verbose_twisted',
            help='debug - show twisted communication')
    store_true('--manhole', dest='use_manhole',
            help='use manhole shell instead of IPython')
    store_true('--nogtk', dest='nogtk',
            help='debug - turn off gtk integration (NOT WORKING)')
    #parser.error = lambda msg: None # only way I know to avoid errors when unknown parameters are given

    # TODO: UNBRAIN DEAD THIS
    # The next part is brain dead, but I don't know how to remove *just*
    # the parameters I used with OptionParser.. delegated option parsers anyone?
    
    def remove_my_args_from_sys_argv():
        todelete = []
        for i, arg in enumerate(sys.argv):
            if arg in storers:
                todelete.extend([i, i+1])
            if arg in true_storers + false_storers:
                todelete.append(i)
        for i in reversed(todelete):
            if i >= len(sys.argv):
                print "bad arguments.. go home"
                raise SystemExit
            del sys.argv[i]

    for group in [main, experimental, debug, unused, pynaoqi]:
        parser.add_option_group(group)

    opts, args = parser.parse_args()
    opts.dt = float(opts.dt)
    ip = opts.ip or get_default_ip()
    ip = host_to_ip(ip)
    port = opts.port or ((ip == '127.0.0.1' and connecting_to_webots() and 9560) or 9559)
    port = int(port)
    opts.starting_team_color = {'blue':BLUE_TEAM, 'yellow':RED_TEAM, 'red':RED_TEAM}.get(
                str(opts.starting_team_color).lower(), opts.starting_team_color)
    # UGLY
    burst_consts.CONSOLE_LINE_LENGTH = int(opts.console_line_length)
    opts.ip = ip
    opts.port = port
    print "VIDEO = opts.video = %s" % opts.video
    return opts, ip, port

LOCALHOST_IP = '127.0.0.1'

def get_default_ip():
    # on the nao the ip should be something that would work - since naoqi by default
    # doesn't listen to the loopback (why? WHY??), we need to find out the public address.
    # "ip route get" does the trick
    ip = LOCALHOST_IP
    try:
        import socket
    except:
        t = os.popen('ip route get 1.1.1.1').read()
        ip = t[t.find('src')+3:].split()[0]
    return ip

def host_to_ip(ip):
    try:
        ip = getaddrinfo(ip, None)[0][4][0]
    except Exception, e:
        print "Warning: can't resolve %r, assuming ip" % ip
    return ip

# defaults are suitable for a locally running naoqi, like on a robot.
ip = get_default_ip()
options, ip, port = parse_command_line_arguments()

# TODO: an ugly twist.
# TODO: just another note that this sucks. Also, target.ip is 'localhost' for pynaoqi,
# but '127.0.0.1' for regular naoqi.
# Now a twist - at the end the ip and port are taken from
# burst_target.ip, burst_target.port .
# if they are not None, we take them as is. This allows for
# working with pynaoqi nicely.

import burst_target
if burst_target.ip is not None:
    ip = burst_target.ip
    port = burst_target.port
else:
    burst_target.ip = ip
    burst_target.port = port

# Two ways to get robot name: If port is 9559 and ip isn't
# '127.0.0.1' (LOCALHOST_IP), then we are connecting remotely,
# and we get the robotname from the ip address.
# On the other hand, if we are connecting locally the ip
# will be 127.0.0.1 and the port 9559, in that case we
# look at the hostname, currently via the "hostname" executable.
if (ip == 'localhost' or ip == LOCALHOST_IP) and port == 9559:
    robotname = os.popen('hostname').read().strip().lower()
elif port == 9560:
    robotname = 'webots'
else:
    robotname = ROBOT_IP_TO_NAME.get(ip, ip)

options.jersey = jersey = int(options.jersey or burst_consts.ROBOT_NAME_TO_JERSEY_NUMBER.get(
    robotname, 1)) # Default to 1
burst_target.robotname = robotname
burst_target.jersey = jersey

def set_all_verbose():
    options.verbose_tracker = True
    options.verbose_eventmanager = True
    options.verbose_localization = True
    options.verbose_movecoordinator = True

print "_"*80
print "You are running with robotname = %s" % robotname
print "-"*80

