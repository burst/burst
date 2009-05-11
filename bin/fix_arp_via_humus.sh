#!/bin/bash
if [ "x$1" == "x" ] ; then
    HOST=maldini
else
    HOST=$1
fi
echo fixing arp via /etc/ethers on $HOST
ssh root@humus.cs.biu.ac.il -- ssh root@$HOST arp -f
