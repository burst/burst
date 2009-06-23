#!/usr/bin/python
import sys, os

if 'AL_DIR' not in os.environ:
    os.environ['AL_DIR'] = '/usr/local/nao'
    print "warning: AL_DIR not defined, defining to %s" % os.environ['AL_DIR']

home = os.environ['HOME']
ld_lib_path='%s/src/burst/lib' % home
if 'LD_LIBRARY_PATH' not in os.environ or ld_lib_path not in os.environ['LD_LIBRARY_PATH']:
    print "warning: %s wasn't in LD_LIBRARY_PATH, adding" % ld_lib_path
    os.environ['LD_LIBRARY_PATH'] = os.environ.get('LD_LIBRARY_PATH', '') + ':' + ld_lib_path

# add path of burst library
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

from burst_util import set_robot_ip_from_argv

def main():
    import pynaoqi.shell as shell
    shell.main()

if __name__ == '__main__':
    print "args = %s" % sys.argv
    set_robot_ip_from_argv()
    main()

