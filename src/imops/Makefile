#
# Makefile for the imops.so shared library that is used from pynaoqi
# and also should be usable from gstreamer / directly with /dev/video0
# later or as a naoqi module.
#

#-DBURST_DEBUG_VISION -DOFFLINE -DDEBUG_IMAGE
CFLAGS_DEBUG=-DOFFLINE -DDEBUG_IMAGE
AL_INC=-I$(AL_DIR)/extern/c/aldebaran/alcommon/soap -I$(AL_DIR)/extern/c/aldebaran/alcommon/interface -I$(AL_DIR)/extern/c/aldebaran/alcommon/include -I$(AL_DIR)/modules/proxies
PY_INC=-I/usr/include/python2.5
CFLAGS=-fPIC -ggdb $(CFLAGS_DEBUG) $(PY_INC) $(AL_INC)
CXXFLAGS=$(CFLAGS)

all: install

install: imops.so
	cp imops.so ../../lib
	cp imops.so $(AL_DIR)/modules/lib/libimops.so

SRC=ConcreteCorner.cpp       ConcreteLine.cpp  Kinematics.cpp       objrec.cpp    Threshold.cpp  VisualBall.cpp      VisualDetection.cpp    VisualLine.cpp \
ConcreteFieldObject.cpp  FieldLines.cpp    NaoPose.cpp          Profiler.cpp  Utility.cpp    VisualCorner.cpp    VisualFieldObject.cpp  VisualRobot.cpp \
ConcreteLandmark.cpp     imops.cpp         ObjectFragments.cpp  Sensors.cpp   Vision.cpp     VisualCrossbar.cpp  VisualLandmark.cpp     Zlib.cpp \
imopsmodule.cpp

OBJ=ConcreteCorner.o       ConcreteLine.o  Kinematics.o       objrec.o    Threshold.o  VisualBall.o      VisualDetection.o    VisualLine.o \
ConcreteFieldObject.o  FieldLines.o    NaoPose.o          Profiler.o  Utility.o    VisualCorner.o    VisualFieldObject.o  VisualRobot.o \
ConcreteLandmark.o     imops.o         ObjectFragments.o  Sensors.o   Vision.o     VisualCrossbar.o  VisualLandmark.o     Zlib.o\
imopsmodule.o

.PHONY: clean

clean:
	rm -f $(OBJ) imops.so

%.cpp,%.o:
	$(CXX) $(CXXCLAGS) -o $% $@

imops.so: $(OBJ)
	g++ -shared -o imops.so $(OBJ)

