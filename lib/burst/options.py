"""
Command line and default config file for BURST robocup platform.
"""

import os
from burst_consts import ROBOT_IP_TO_NAME
import burst_consts

__all__ = ['running_on_nao', 'connecting_to_webots', 'connecting_to_nao',
    'options', 'ip', 'port']

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
    global ip
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
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('', '--ip', dest='ip', help='ip address for broker, default is localhost')
    parser.add_option('', '--port', dest='port', help='port used by broker, localhost will default to 9560, rest to 9559')
    parser.add_option('', '--pynaoqi', action='store_true', dest='use_pynaoqi', help='use pynaoqi and twisted (TESTING)')
    parser.add_option('', '--bodyposition', dest='bodyposition', help='test app: prints bodyposition continuously')
    parser.add_option('', '--profile', action='store_true', dest='profile', default=False, help='profile the application')
    parser.add_option('', '--unsafe', action='store_false', dest='catch_player_exceptions', default=True, help='don\'t catch stray exceptions')
    parser.add_option('', '--traceproxies', action='store_true', dest='trace_proxies', default=False, help='trace proxy calls')
    parser.add_option('', '--logpositions', action='store_true', dest='log_positions', default=False, help='will record positions of objects into csv files in the current directory, with timestamps')
    parser.add_option('', '--passivectrlc', action='store_true', dest='passive_ctrl_c', default=False, help='Don\'t do initPoseAndRelax on Ctrl-C')
    parser.add_option('', '--debugpersonal', action='store_true', dest='debug_personal', default=False, help='Remove try around __import__(personal)')
    parser.add_option('', '--verbose-tracker', action='store_true', dest='verbose_tracker', default=False, help='Verbose tracker/searcher/center')
    parser.add_option('', '--verbose-eventmanager', action='store_true', dest='verbose_eventmanager', default=False, help='Verbose event manager')
    parser.add_option('', '--verbose-localization', action='store_true', dest='verbose_localization', default=False, help='Verbose localization')
    parser.add_option('', '--runultrasound', action='store_true', dest='run_ultrasound', default=False, help='Run UltraSound')
    parser.add_option('', '--debug', action='store_true', dest='debug', default=False, help='Turn on debugging code')
    parser.add_option('', '--console-line-length', action='store', dest='console_line_length', default=burst_consts.CONSOLE_LINE_LENGTH, help='allow for wider/leaner screen debugging')
    opts, args = parser.parse_args()
    ip = opts.ip or get_default_ip()
    ip = host_to_ip(ip)
    port = opts.port or ((ip == '127.0.0.1' and connecting_to_webots() and 9560) or 9559)
    port = int(port)
    globals()['ip'] = ip
    globals()['port'] = port
    globals()['options'] = opts
    # UGLY
    burst_consts.CONSOLE_LINE_LENGTH = int(opts.console_line_length)

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

# defaults - suitable for a locally running naoqi, like on a robot.
ip = get_default_ip()
port = 9559
# now override them (possibly)
parse_command_line_arguments()

# Now a twist - at the end the ip and port are taken from
# burst_target.ip, burst_target.port
# if they are not None, we take them as is. This allows for
# working with pynaoqi nicely.

import burst_target
if burst_target.ip is not None:
    ip = burst_target.ip
    port = burst_target.port

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

burst_target.robotname = robotname

print "_"*80
print "You are running with robotname = %s" % robotname
print "-"*80

