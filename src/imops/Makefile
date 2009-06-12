#
# Makefile for the imops.so shared library that is used from pynaoqi
# and also should be usable from gstreamer / directly with /dev/video0
# later or as a naoqi module.
#

# Rules explanation:
#
# There are three build directories for the four targets:
#  host 32bit <- webots 32 bit + pynaoqi
#  host 64bit <- pynaoqi 64 bit
#  robot      <- robot
#
# This works by calling my self from the main targets after chdir
# to the build dir, and setting VPATH to contain the original directory.
#
# The main targets are:
#  robot - cross compile and install for the robot (cross is the same as robot)
#  pynaoqi - compile and install the pynaoqi module, regardless of word size
#  webots - compile and install the webots module, will complain if in 64 bit environment.
#
# compilation results will always end up in the BUILD dir, which is
#  build_host32, build_host64 or build_robot
# 

# Possible debug flags:
# TODO - document function of each
#-DBURST_DEBUG_VISION -DOFFLINE -DDEBUG_IMAGE

# BURST_DEBUG_VISION - print vision related stuff
# BURST_DEBUG_VISION_THREAD - prints time per loop, and frame count

# Burst flags:
# BURST_DO_LOCALIZATION_IN_MODULE - not working right now (or ever?)

ifdef ROOT
include $(ROOT)/Makefile.local
endif

VPATH=$(srcdir)

all: cross

# Flags for debug and release builds. host builds are always debug.
DEBUG_BUILD=-fPIC -ggdb
# ok, there is a -march=geode but only in newer g++.
RELEASE_BUILD=-O3 -DNDEBUG -Wall -Wno-unused -Wno-strict-aliasing -march=k6-2 -mtune=k6-2

# Turn on any debug flags - same for all targets
CFLAGS_DEBUG=

# shared library names are:
# imops_host_32.so - 32 bit for host
# imops_host_64.so - 64 bit for host
# imops.so - robot version (32 bit, compiled with aldebaran toolchain)

ROBOT_BUILD_DIR=build_robot
HOST_32_BUILD_DIR=build_host_32
HOST_64_BUILD_DIR=build_host_64

# Big Build Switch
ifeq ($(BUILD),HOST32)
# 32 host
BUILD_DIR=$(HOST_32_BUILD_DIR)
IMOPS_WEBOTS_TARGET=imops_host_32.so
IMOPS_PYNAOQI_TARGET=imops_pynaoqi_32.so

BASE_CFLAGS=-DWEBOTS=1
BUILD_CFLAGS=$(DEBUG_BUILD)
CFLAGS_DEBUG_BUILD=-DOFFLINE -DDEBUG_IMAGE
PY_INC=-I/usr/include/python2.5
else
ifeq ($(BUILD),HOST64)
# 64 host
BUILD_DIR=$(HOST_64_BUILD_DIR)
IMOPS_WEBOTS_TARGET=imops_host_64.so
IMOPS_PYNAOQI_TARGET=imops_pynaoqi_64.so

BASE_CFLAGS=
BUILD_CFLAGS=$(DEBUG_BUILD)
CFLAGS_DEBUG_BUILD=-DOFFLINE -DDEBUG_IMAGE
PY_INC=-I/usr/include/python2.5
else
# robot
$(info COMPILING FOR ROBOT)
BUILD_DIR=$(ROBOT_BUILD_DIR)
STAGING=$(AL_DIR)/crosstoolchain/staging
CC=$(AL_DIR)/crosstoolchain/cross/bin/i486-linux-gcc
CXX=$(AL_DIR)/crosstoolchain/cross/bin/i486-linux-g++
# TODO - this cannot be the right way to do this.
BASE_CFLAGS=--sysroot $(STAGING)/i486-linux/ -I$(STAGING)/i486-linux/usr/include/c++/i486-linux -I$(STAGING)/i486-linux/usr/include/c++/
PY_INC=-I$(STAGING)/i486-linux/usr/include/python2.5/
ifeq ($(DEBUG),1)
BUILD_CFLAGS=$(DEBUG_BUILD)
else
BUILD_CFLAGS=$(RELEASE_BUILD)
endif
#AL_INC
CFLAGS_DEBUG_BUILD=
endif
endif

# ARCH is used for setting BUILD when calling ourselves.
ARCH=$(shell uname -m)
ifeq ($(ARCH),x86_64)
IS64=1
HOST_BUILD=HOST64
HOST_BUILD_DIR=$(HOST_64_BUILD_DIR)
else
IS64=0
HOST_BUILD=HOST32
HOST_BUILD_DIR=$(HOST_32_BUILD_DIR)
endif

# Flags originally found in Northern Bites.
# all are in manconfig.h anyway (at least USE_VISION is)
# The following are from VERBOSE=1 when doing a make in nao-man:
# NO_ZLIB - I guess affects the initTable?
# WITH_NOIDREF - no idea
# ROBOT_TYPE=NAO_RL - well, seems ok
# -DTRUNK_REVISION="\"rr0\"" - ??
# -pthread - TODO read help!
# -Wno-write-strings - TODO
NB_FLAGS=-DNO_ZLIB -DWITH_NOIDREF -DROBOT_TYPE=NAO_RL -pthread -Wno-write-strings -DTRUNK_REVISION="\"rr0\""
AL_INC=-I$(AL_DIR)/extern/c/aldebaran/alcommon/soap -I$(AL_DIR)/extern/c/aldebaran/alcommon/interface -I$(AL_DIR)/extern/c/aldebaran/alcommon/include -I$(AL_DIR)/modules/proxies
CFLAGS=$(BUILD_CFLAGS) $(BASE_CFLAGS) $(NB_FLAGS) $(CFLAGS_DEBUG) $(CFLAGS_DEBUG_BUILD) $(PY_INC) $(AL_INC)
CXXFLAGS=$(CFLAGS)
LDFLAGS=-lz

SRC=ConcreteCorner.cpp       ConcreteLine.cpp  Kinematics.cpp       objrec.cpp    Threshold.cpp  VisualBall.cpp      VisualDetection.cpp    VisualLine.cpp \
ConcreteFieldObject.cpp  FieldLines.cpp    NaoPose.cpp          Profiler.cpp  Utility.cpp    VisualCorner.cpp    VisualFieldObject.cpp  VisualRobot.cpp \
ConcreteLandmark.cpp     imops.cpp         ObjectFragments.cpp  Sensors.cpp   Vision.cpp     VisualCrossbar.cpp  VisualLandmark.cpp     Zlib.cpp \
imopsmodule.cpp ALImageTranscriber.cpp synchro.cpp

OBJ=$(SRC:.cpp=.o)

OBJ_PYNAOQI=ConcreteCorner.o       ConcreteLine.o  Kinematics.o       objrec.o    Threshold.o  VisualBall.o      VisualDetection.o    VisualLine.o \
ConcreteFieldObject.o  FieldLines.o    NaoPose.o          Profiler.o  Utility.o    VisualCorner.o    VisualFieldObject.o  VisualRobot.o \
ConcreteLandmark.o     imops.o         ObjectFragments.o  Sensors.o   Vision.o     VisualCrossbar.o  VisualLandmark.o     Zlib.o

# Localization - right now done in burst code (out in python land)
LOC_SRC=BallEKF.cpp Observation.cpp
LOC_OBJ=BallEKF.o Observation.h

.PHONY: clean clean_robot clean_32 clean_64

clean: clean_robot clean_32 clean_64

clean_robot:
	cd $(ROBOT_BUILD_DIR); rm -f $(OBJ) *.so

clean_32:
	cd $(HOST_32_BUILD_DIR); rm -f $(OBJ) *.so

clean_64:
	cd $(HOST_64_BUILD_DIR); rm -f $(OBJ) *.so

# This is not really used right now.
precompiled.h.gch: precompiled.h
	$(CXX) $(CXXFLAGS) -o $@ $<

%.cpp,%.o: %.cpp
	$(CXX) $(CXXCLAGS) -o $@ $<

# We have three targets, for three uses:
# 64bit for pynaoqi
# 32bits webots and pynaoqi on 32 bit systems
# cross for robot (this is just standard 32bit but different flags maybe, and different toolchain)

$(IMOPS_WEBOTS_TARGET): $(OBJ)
	$(CXX) -shared $(LDFLAGS) $(CXXFLAGS) -o $(IMOPS_WEBOTS_TARGET) $(OBJ)

imops.so: $(OBJ)
	$(CXX) -shared $(LDFLAGS) $(CXXFLAGS) -o imops.so $(OBJ)

$(IMOPS_PYNAOQI_TARGET): $(OBJ_PYNAOQI)
	$(CXX) -shared $(LDFLAGS) $(CXXFLAGS) -o $(IMOPS_PYNAOQI_TARGET) $(OBJ_PYNAOQI)

$(HOST_BUILD_DIR):
	mkdir -p $(HOST_BUILD_DIR)

$(ROBOT_BUILD_DIR):
	mkdir -p $(ROBOT_BUILD_DIR)

################################################################################
# Main Targets

# TODO - cannot move this to the top, it breaks the makefile.

.PHONY: webots cross robot pynaoqi

# Compile and build for the robot.

robot: cross

cross: $(ROBOT_BUILD_DIR)
	cd $(ROBOT_BUILD_DIR); $(MAKE) -f ../Makefile cross_helper BUILD=ROBOT DEBUG=0 srcdir=../ ROOT=../../../

crossdebug: $(ROBOT_BUILD_DIR)
	cd $(ROBOT_BUILD_DIR); $(MAKE) -f ../Makefile cross_helper BUILD=ROBOT DEBUG=1

cross_helper: imops.so
	scp imops.so root@$(ROBOT):/opt/naoqi/modules/lib/libimops.so


# pynaoqi

pynaoqi: $(HOST_BUILD_DIR)
	cd $(HOST_BUILD_DIR); $(MAKE) -f ../Makefile pynaoqi_helper BUILD=$(HOST_BUILD) srcdir=../ ROOT=../../../

pynaoqi_helper: $(IMOPS_PYNAOQI_TARGET)
	cp $(IMOPS_PYNAOQI_TARGET) ../../../lib

# webots

ifeq ($(IS64),1)
webots:
	@echo you cannot build the webots target in 64 bit - try a chroot
else
webots:
	mkdir -p $(HOST_BUILD_DIR)
	cd $(HOST_BUILD_DIR); $(MAKE) -f ../Makefile webots_helper BUILD=$(HOST_BUILD) srcdir=../ ROOT=../../../
endif

webots_helper: $(IMOPS_WEBOTS_TARGET)
	cp $(IMOPS_WEBOTS_TARGET) $(AL_DIR)/modules/lib/libimops.so

################################################################################


