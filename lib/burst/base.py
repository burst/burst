"""
if on a 32 bit code base:
    finds naoqi, fixes sys.path and then imports it.
else:
    currently does nothing
"""

# Test where we are - could be one of simulator, on robot, or remote.
# there is no actual difference between simulator and remote, or actually
# robot - as long as we use the AL_DIR variable. If it doesn't exist, try
# looking in a few default places (but we really should be setting AL_DIR
# all arround - so this is probably a good occasion to use syslog to scream
# at our users).

from . import debug

from burst_util import is64

predefined_sys_paths = [
 # opennao (as came with the robots)
('/opt/naoqi/extern/python/aldebaran',
 '/opt/naoqi/extern/python/aldebaran/geode'
 ),
]

LOCALHOST_IP = '127.0.0.1'

import os
import sys
try: # doesn't work on opennao
    from socket import getaddrinfo # for resolving a hostname
except:
    getaddrinfo = lambda ip, port: [[None, None, None, [ip]]]

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

def fix_sys_path():
    naoqi_root = None
    al_dir = os.environ.get('AL_DIR', None)
    if al_dir != None:
        if not os.path.exists(al_dir):
            print "AL_DIR set to nonexistant path!\nAL_DIR = %s\nQuitting." % al_dir
            raise SystemExit
        base = os.path.join(al_dir, 'extern', 'python')
        dirpath, dirnames, filenames = os.walk(base).next()
        for dirpath in dirnames:
            if os.path.split(dirpath)[-1] != 'proxies':
                second = os.path.join(base, dirpath)
                break
        predefined_sys_paths.insert(0, (base, os.path.join(base, 'aldebaran'), second))
    for paths in predefined_sys_paths:
        if all([os.path.exists(path) for path in paths]):
            sys.path.extend(paths)
            naoqi_root = paths[0]
            naoqi_imp = paths[1]
            break
    if naoqi_root is None:
        print """ERROR: naoqi is not installed. Please install it and make sure the AL_DIR environment
variable points to it. See https://shwarma.cs.biu.ac.il/moin/NaoQi for OS specific instructions
"""
        raise SystemExit


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

# defaults - suitable for a locally running naoqi, like on a robot.
ip = get_default_ip()
port = 9559

def host_to_ip(ip):
    try:
        ip = getaddrinfo(ip, None)[0][4][0]
    except Exception, e:
        print "Warning: can't resolve %r, assuming ip" % ip
    return ip

def parse_command_line_arguments():
    import sys
    if not hasattr(sys, 'argv'): # fix for bug when importing from within nao-man
        sys.argv=['fake']
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-i', '--ip', dest='ip', help='ip address for broker, default is localhost')
    parser.add_option('-p', '--port', dest='port', help='port used by broker, localhost will default to 9560, rest to 9559')
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

parse_command_line_arguments()

# Set path only after reading command line arguments - we need them to know
# if we are connecting to a simulator.

def find_naoqi():
    try:
        from aldebaran import naoqi
    except:
        try:
            import naoqi
        except:
            pass

    if 'naoqi' not in sys.modules and 'aldebaran' not in sys.modules:
        fix_sys_path()

    print_warning = False
    try:
        from aldebaran import naoqi
    except:
        try:
            import naoqi
        except Exception, e:
            print "naoqi import caused exception (after path fix):", e
            print_warning = True
        except:
            print_warning = True

    if print_warning:
        print "burst did it's best to find naoqi - you are probably either"
        print "forgetting to setup AL_DIR or on a 64 bit machine. Either way"
        print "burst will let you continue, but expect everything to explode."


# maybe this is already taken care of? test first.
if is64():
    print "burst.base - 64 bit architecture, not looking for naoqi"
else:
    find_naoqi()


