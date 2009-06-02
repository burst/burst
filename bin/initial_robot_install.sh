#!/bin/bash

ROBOT=root@$1
LIBRARIES="$AL_DIR/crosstoolchain/staging/i486-linux/usr/lib/libboost_python-mt.so $AL_DIR/crosstoolchain/staging/i486-linux/usr/lib/libboost_signals-mt.so"
BIN_FILES=`which arp`
SCRIPTS=watchlog

echo copying $LIBRARIES
scp $LIBRARIES $ROBOT:/usr/lib
echo copying python files
scp /usr/lib/python2.5/pickle.py /usr/lib/python2.5/struct.py /usr/lib/python2.5/re.py /usr/lib/python2.5/sre_compile.py /usr/lib/python2.5/sre_constants.py /usr/lib/python2.5/sre_parse.py $ROBOT:/usr/lib/python2.5/
echo copying $BIN_FILES
scp $BIN_FILES $ROBOT:/usr/bin
echo copying some scripts
scp $SCRIPTS $ROBOT:/usr/bin
echo copying ini file reset on boot script
scp autoload_init $ROBOT:/etc/init.d
ssh $ROBOT ln -sf /etc/init.d/autoload_init /etc/rc5.d/S55autoload_init

