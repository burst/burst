#
# Makefile for the imops.so shared library that is used from pynaoqi
# and also should be usable from gstreamer / directly with /dev/video0
# later or as a naoqi module.
#

# Possible debug flags:
# TODO - document function of each
#-DBURST_DEBUG_VISION -DOFFLINE -DDEBUG_IMAGE

# BURST_DEBUG_VISION - print vision related stuff
# BURST_DEBUG_VISION_THREAD

# Burst flags:
# BURST_DO_LOCALIZATION_IN_MODULE - not working right now (or ever?)

include ../../Makefile.local

DEBUG_BUILD=-fPIC -ggdb
# ok, there is a -march=geode but only in newer g++.
RELEASE_BUILD=-O3 -march=i586

CFLAGS_DEBUG=

# defaults - overridden if 

ifdef BUILD
# TODO - broken;
# if BUILD is defined we assume you want a release build, otherwise a debug.
STAGING=$(AL_DIR)/crosstoolchain/staging
BUILD=$(RELEASE_BUILD)
CC=$(AL_DIR)/crosstoolchain/cross/bin/i486-linux-gcc
CXX=$(AL_DIR)/crosstoolchain/cross/bin/i486-linux-g++
# TODO - this cannot be the right way to do this.
BASE_CFLAGS=--sysroot $(STAGING)/i486-linux/ -I$(STAGING)/i486-linux/usr/include/c++/i486-linux -I$(STAGING)/i486-linux/usr/include/c++/
PY_INC=-I$(STAGING)/i486-linux/usr/include/python2.5/
#AL_INC
CFLAGS_DEBUG_BUILD=
else
BASE_CFLAGS=
BUILD=$(DEBUG_BUILD)
CFLAGS_DEBUG_BUILD=-DOFFLINE -DDEBUG_IMAGE
PY_INC=-I/usr/include/python2.5
endif

# Flags originally found in Northern Bites.
# all are in manconfig.h anyway (at least USE_VISION is)
NB_FLAGS=
AL_INC=-I$(AL_DIR)/extern/c/aldebaran/alcommon/soap -I$(AL_DIR)/extern/c/aldebaran/alcommon/interface -I$(AL_DIR)/extern/c/aldebaran/alcommon/include -I$(AL_DIR)/modules/proxies
CFLAGS=$(BUILD) $(BASE_CFLAGS) $(NB_FLAGS) $(CFLAGS_DEBUG) $(CFLAGS_DEBUG_BUILD) $(PY_INC) $(AL_INC)
CXXFLAGS=$(CFLAGS)
LDFLAGS=-lz

all: imops_pynaoqi.so

install: imops.so
	cp imops.so $(AL_DIR)/modules/lib/libimops.so

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

.PHONY: clean

clean:
	rm -f $(OBJ) imops.so

precompiled.h.gch: precompiled.h
	$(CXX) $(CXXFLAGS) -o $@ $<

%.cpp,%.o: %.cpp
	$(CXX) $(CXXCLAGS) -o $@ $<

imops.so: $(OBJ)
	$(CXX) -shared $(LDFLAGS) $(CXXFLAGS) -o imops.so $(OBJ)

imops_pynaoqi.so: $(OBJ_PYNAOQI)
	$(CXX) -shared $(LDFLAGS) $(CXXFLAGS) -o imops_pynaoqi.so $(OBJ_PYNAOQI)
	cp imops_pynaoqi.so ../../lib

# Compile and build for webots - just the usual with an additional copy rule
webots: imops.so
	cp imops.so $(AL_DIR)/modules/lib/libimops.so

# Compile and build for the robot.
# Uses cross_helper to set the flags as a release build
# (if we want a debug build, needs a little work - maybe
# just a cross_debug target)
cross:
	$(MAKE) cross_helper BUILD="$(RELEASE_BUILD)"

crossdebug:
	$(MAKE) cross_helper BUILD="$(DEBUG_BUILD)"


cross_helper: imops.so
	scp imops.so root@$(ROBOT):/opt/naoqi/modules/lib/libimops.so

