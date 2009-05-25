"""
Command line and default config file for BURST robocup platform.
"""

import os

__all__ = ['running_on_nao', 'connecting_to_webots', 'connecting_to_nao',
    'options', 'ip', 'port']

try: # doesn't work on opennao
    from socket import getaddrinfo # for resolving a hostname
except:
    getaddrinfo = lambda ip, port: [[None, None, None, [ip]]]
    print "WARNING: socket is missing. Did you follow https://shwarma.cs.biu.ac.il/moin/InstallingNaoMan?"

def running_on_nao():
    """ True if we are physically on the nao geode brain box """
    return os.path.exists('/opt/naoqi/bin/naoqi')

def connecting_to_webots():
    """ True if we are connecting to webots """
    global ip
    #is_nao = os.popen("uname -m").read().strip() == 'i586'
    return not running_on_nao() and ip == LOCALHOST_IP

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
    opts, args = parser.parse_args()
    ip = opts.ip or get_default_ip()
    ip = host_to_ip(ip)
    port = opts.port or ((ip == '127.0.0.1' and connecting_to_webots() and 9560) or 9559)
    port = int(port)
    globals()['ip'] = ip
    globals()['port'] = port
    globals()['options'] = opts

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

# Two ways to get robot name: If port is 9559 and ip isn't
# '127.0.0.1' (LOCALHOST_IP), then we are connecting remotely,
# and we get the robotname from the ip address.
# On the other hand, if we are connecting locally the ip
# will be 127.0.0.1 and the port 9559, in that case we
# look at the hostname, currently via the "hostname" executable.
if ip == LOCALHOST_IP and port == 9559:
    robotname = os.popen('hostname').read().strip().lower()
elif port == 9560:
    robotname = 'webots'
else:
    robotname = {
        '192.168.7.106'	: 'messi',
        '192.168.7.107'	: 'gerrard',
        '192.168.7.108'	: 'cech',
        '192.168.7.177'	: 'hagi',
        '192.168.7.109'	: 'raul',
        '192.168.7.110'	: 'maldini',
    }.get(ip, ip)

print "_"*80
print "You are running with robotname = %s" % robotname
print "-"*80

