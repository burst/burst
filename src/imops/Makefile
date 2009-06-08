#
# Makefile for the imops.so shared library that is used from pynaoqi
# and also should be usable from gstreamer / directly with /dev/video0
# later or as a naoqi module.
#

# Possible debug flags:
# TODO - document function of each
#-DBURST_DEBUG_VISION -DOFFLINE -DDEBUG_IMAGE

# Burst flags:
# BURST_DO_LOCALIZATION_IN_MODULE - not working right now (or ever?)

CFLAGS_DEBUG=-DOFFLINE -DDEBUG_IMAGE
# Flags originally found in Northern Bites.
# all are in manconfig.h anyway (at least USE_VISION is)
NB_FLAGS=
AL_INC=-I$(AL_DIR)/extern/c/aldebaran/alcommon/soap -I$(AL_DIR)/extern/c/aldebaran/alcommon/interface -I$(AL_DIR)/extern/c/aldebaran/alcommon/include -I$(AL_DIR)/modules/proxies
PY_INC=-I/usr/include/python2.5
CFLAGS=-fPIC -ggdb $(NB_FLAGS) $(CFLAGS_DEBUG) $(PY_INC) $(AL_INC)
CXXFLAGS=$(CFLAGS)

all: imops_pynaoqi.so

install: imops.so
	cp imops.so $(AL_DIR)/modules/lib/libimops.so

SRC=ConcreteCorner.cpp       ConcreteLine.cpp  Kinematics.cpp       objrec.cpp    Threshold.cpp  VisualBall.cpp      VisualDetection.cpp    VisualLine.cpp \
ConcreteFieldObject.cpp  FieldLines.cpp    NaoPose.cpp          Profiler.cpp  Utility.cpp    VisualCorner.cpp    VisualFieldObject.cpp  VisualRobot.cpp \
ConcreteLandmark.cpp     imops.cpp         ObjectFragments.cpp  Sensors.cpp   Vision.cpp     VisualCrossbar.cpp  VisualLandmark.cpp     Zlib.cpp \
imopsmodule.cpp ALImageTranscriber.cpp synchro.cpp

OBJ=ConcreteCorner.o       ConcreteLine.o  Kinematics.o       objrec.o    Threshold.o  VisualBall.o      VisualDetection.o    VisualLine.o \
ConcreteFieldObject.o  FieldLines.o    NaoPose.o          Profiler.o  Utility.o    VisualCorner.o    VisualFieldObject.o  VisualRobot.o \
ConcreteLandmark.o     imops.o         ObjectFragments.o  Sensors.o   Vision.o     VisualCrossbar.o  VisualLandmark.o     Zlib.o\
imopsmodule.o ALImageTranscriber.o synchro.o

OBJ_PYNAOQI=ConcreteCorner.o       ConcreteLine.o  Kinematics.o       objrec.o    Threshold.o  VisualBall.o      VisualDetection.o    VisualLine.o \
ConcreteFieldObject.o  FieldLines.o    NaoPose.o          Profiler.o  Utility.o    VisualCorner.o    VisualFieldObject.o  VisualRobot.o \
ConcreteLandmark.o     imops.o         ObjectFragments.o  Sensors.o   Vision.o     VisualCrossbar.o  VisualLandmark.o     Zlib.o

# Localization - right now done in burst code (out in python land)
LOC_SRC=BallEKF.cpp Observation.cpp
LOC_OBJ=BallEKF.o Observation.h

.PHONY: clean

clean:
	rm -f $(OBJ) imops.so

%.cpp,%.o:
	$(CXX) $(CXXCLAGS) -o $% $@

imops.so: $(OBJ)
	g++ -shared -o imops.so $(OBJ)

imops_pynaoqi.so: $(OBJ_PYNAOQI)
	g++ -shared -o imops_pynaoqi.so $(OBJ_PYNAOQI)
	cp imops_pynaoqi.so ../../lib

