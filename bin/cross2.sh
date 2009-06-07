#!/bin/sh
##
## @author Cedric GESTES
## Aldebaran Robotics (c) 2008 All Rights Reserved
##
## Version : $Id$
##

#
# -- how to compile --
# - setup your env:
#    source cross-compil-env.sh /directoryofyourcrosstoolchain
#
# - configure your project if you use autotools:
#    ./configure --host=i486-linux --target=i486-linux
#
# - build your project:
# make
#
# make install prefix=/var/tmp/mypackage
#
# then copy what you need from mypackage on the robot.
#

export CROSS_COMPIL_DIR=$CTC_DIR

export CC=${CROSS_COMPIL_DIR}/cross/bin/i486-linux-gcc
export CXX=${CROSS_COMPIL_DIR}/cross/bin/i486-linux-g++
export AR=${CROSS_COMPIL_DIR}/cross/bin/i486-linux-ar
export RANLIB=${CROSS_COMPIL_DIR}/cross/bin/i486-linux-ranlib
export LD=${CROSS_COMPIL_DIR}/cross/bin/i486-linux-ld
export STRIP=${CROSS_COMPIL_DIR}/cross/bin/i486-linux-strip
export OBJCOPY=${CROSS_COMPIL_DIR}/cross/bin/i486-linux-objcopy
export OBJDUMP=${CROSS_COMPIL_DIR}/cross/bin/i486-linux-objdump

export CPPFLAGS="--sysroot ${CROSS_COMPIL_DIR}/staging/i486-linux/ \
-I${CROSS_COMPIL_DIR}/staging/i486-linux/usr/include/ \
-I${CROSS_COMPIL_DIR}/cross/lib/gcc/i486-linux/4.2.2/include/ \
-I${CROSS_COMPIL_DIR}/staging/i486-linux/usr/include/c++/ \
-I${CROSS_COMPIL_DIR}/staging/i486-linux/usr/include/c++/i486-linux/"

export CFLAGS="--sysroot ${CROSS_COMPIL_DIR}/staging/i486-linux/ \
-I${CROSS_COMPIL_DIR}/staging/i486-linux/usr/include/ \
-I${CROSS_COMPIL_DIR}/cross/lib/gcc/i486-linux/4.2.2/include/ \
-I${CROSS_COMPIL_DIR}/staging/i486-linux/usr/include/c++/ \
-I${CROSS_COMPIL_DIR}/staging/i486-linux/usr/include/c++/i486-linux/"

export LDFLAGS="--sysroot ${CROSS_COMPIL_DIR}/staging/i486-linux/ \
-lgcc -L${CROSS_COMPIL_DIR}/cross/i486-linux/lib/ -lc -lstdc++ -ldl"

export PKG_CONFIG_SYSROOT_DIR="${CROSS_COMPIL_DIR}/staging/i486-linux"
export PKG_CONFIG_PATH="${CROSS_COMPIL_DIR}/staging/i486-linux"
export PKG_CONFIG_DIR="${CROSS_COMPIL_DIR}/staging/i486-linux/usr/lib/pkgconfig"

export PATH="${CROSS_COMPIL_DIR}/staging/i686-linux/usr/bin/i486-linux:\
${CROSS_COMPIL_DIR}/staging/i686-linux/usr/sbin:\
${CROSS_COMPIL_DIR}/staging/i686-linux/usr/bin:\
${CROSS_COMPIL_DIR}/cross/bin:\
${CROSS_COMPIL_DIR}/staging/i686-linux/sbin:\
${CROSS_COMPIL_DIR}/staging/i686-linux/bin/:\
$PATH"

