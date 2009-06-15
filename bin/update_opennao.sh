export ROBOT=root@$1
echo ROBOT=$ROBOT
#TODO - try to ping
scp $AL_DIR/crosstoolchain/staging/i486-linux/usr/lib/libboost_python-mt.so $ROBOT:/usr/lib
scp $AL_DIR/crosstoolchain/staging/i486-linux/usr/lib/libboost_signals-mt.so $ROBOT:/usr/lib

echo The rest should be done with rsync - see shwarma wiki
exit -1
# used by debugsocket?
LIST1="/usr/lib/python2.5/pickle.py /usr/lib/python2.5/struct.py /usr/lib/python2.5/re.py /usr/lib/python2.5/sre_compile.py /usr/lib/python2.5/sre_constants.py /usr/lib/python2.5/sre_parse.py"
# used by debugsocket, definitely
LIST2="/usr/lib/python2.5/lib-dynload/_socket.so /usr/lib/python2.5/socket.py /usr/lib/python2.5/code.py /usr/lib/python2.5/codeop.py /usr/lib/python2.5/traceback.py /usr/lib/python2.5/StringIO.py"
# used by burst (on top of possibly the previous ones)
LIST3="/usr/lib/python2.5/textwrap.py /usr/lib/python2.5/optparse.py /usr/lib/python2.5/string.py"
# These are needed by pynaoqi - not sure we should have them there by default.. need to see how much place it takes.
LIST4="/usr/lib/python2.5/base64.py /usr/lib/python2.5/urllib2.py /usr/lib/python2.5/hashlib.py /usr/lib/python2.5/httplib.py /usr/lib/python2.5/mimetools.py /usr/lib/python2.5/rfc822.py /usr/lib/python2.5/tempfile.py /usr/lib/python2.5/urlparse.py /usr/lib/python2.5/bisect.py /usr/lib/python2.5/urllib.py"
DYN_LIST="/usr/lib/python2.5/lib-dynload/datetime.so /usr/lib/python2.5/lib-dynload/_hashlib.so"

scp $LIST1 $LIST2 $LIST3 $LIST4 $ROBOT:/usr/lib/python2.5/
scp -r /usr/lib/python2.5/xml $ROBOT:/usr/lib/python2.5/
scp $DYN_LIST  $ROBOT:/usr/lib/python2.5/lib-dynload
