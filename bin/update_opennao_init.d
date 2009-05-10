#!/bin/bash
export ROBOT=$1
if [ "x$1" == "x" ]; then
 echo please supply robot hostname/ip
 exit -1
fi

scp init.d/autoload_init root@$ROBOT:/etc/init.d
ssh root@$ROBOT ln -sf /etc/init.d/autoload_init /etc/rc5.d/S55autoload_init
