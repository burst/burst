"""
finds naoqi, fixes sys.path and then imports it.
"""

# Test where we are - could be one of simulator, on robot, or remote.
# there is no actual difference between simulator and remote, or actually
# robot - as long as we use the AL_DIR variable. If it doesn't exist, try
# looking in a few default places (but we really should be setting AL_DIR
# all arround - so this is probably a good occasion to use syslog to scream
# at our users).

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

def connecting_to_webots():
    global ip
    is_nao = os.popen("uname -m").read().strip() == 'i586'
    return not is_nao and ip == LOCALHOST_IP

def fix_sys_path():
    naoqi_root = None
    al_dir = os.environ.get('AL_DIR', None)
    if al_dir != None:
        if not os.path.exists(al_dir):
            print "AL_DIR set to nonexistant path!\nAL_DIR = %s\nQuitting." % al_dir
            raise SystemExit
        base = os.path.join(al_dir, 'extern', 'python', 'aldebaran')
        dirpath, dirnames, filenames = os.walk(base).next()
        for dirpath in dirnames:
            if os.path.split(dirpath)[-1] != 'proxies':
                second = os.path.join(base, dirpath)
                break
        predefined_sys_paths.insert(0, (base, second))
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


from getopt import gnu_getopt

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

def parse_command_line_arguments():
    global ip, port
    opts, args = gnu_getopt(sys.argv[1:], '', ['ip=', 'port=', 'bodyposition'])
    for k, v in opts:
        if k == '--ip':
            ip = v
            # harmless if already an ip
            try:
                ip = getaddrinfo(ip, None)[0][4][0]
            except Exception, e:
                print "Warning: can't resolve %r, assuming ip" % ip
        elif k == '--port':
            port = int(v)
    globals()['ip'] = ip
    globals()['port'] = port

try:
    parse_command_line_arguments()
except Exception, e:
    if debug:
        import pdb; pdb.set_trace()

# Set path only after reading command line arguments - we need them to know if we are connecting
# to a simulator.

# maybe this is already taken care of? test first.
try:
    import naoqi
except:
    pass

if 'naoqi' not in sys.modules:
    fix_sys_path()

import naoqi

