#
# Copyright 2002,2003 Sony Corporation 
#
# Permission to use, copy, modify, and redistribute this software for
# non-commercial use is hereby granted.
#
# This software is provided "as is" without warranty of any kind,
# either expressed or implied, including but not limited to the
# implied warranties of fitness for a particular purpose.
#

OPENRSDK_ROOT?=/usr/local/OPEN_R_SDK
INSTALLDIR=../MS
CXX=$(OPENRSDK_ROOT)/bin/mipsel-linux-g++
STRIP=$(OPENRSDK_ROOT)/bin/mipsel-linux-strip
MKBIN=$(OPENRSDK_ROOT)/OPEN_R/bin/mkbin
STUBGEN=$(OPENRSDK_ROOT)/OPEN_R/bin/stubgen2
MKBINFLAGS=-p $(OPENRSDK_ROOT)
LIBS=-L$(OPENRSDK_ROOT)/OPEN_R/lib -lObjectComm -lOPENR -lInternet -lantMCOOP
CXXFLAGS= \
	-O2 \
	-g \
	-I. \
	-I$(OPENRSDK_ROOT)/OPEN_R/include/R4000 \
	-I$(OPENRSDK_ROOT)/OPEN_R/include/MCOOP \
	-I$(OPENRSDK_ROOT)/OPEN_R/include

#
# When OPENR_DEBUG is defined, OSYSDEBUG() is available.
#
# CXXFLAGS+= -DOPENR_DEBUG

.PHONY: all install clean

all: GameController.bin

%.o: %.cc
	$(CXX) $(CXXFLAGS) -o $@ -c $^

GameControllerStub.cc: stub.cfg
	$(STUBGEN) stub.cfg	

GameController.bin: GameControllerStub.o GameController.o GameController.ocf
	$(MKBIN) $(MKBINFLAGS) -o $@ $^ $(LIBS)
	$(STRIP) $@

install: GameController.bin
	gzip -c GameController.bin > $(INSTALLDIR)/OPEN-R/MW/OBJS/GAMECTRL.BIN

clean:
	rm -f *.o *.bin *.elf *.snap.cc
	rm -f GameControllerStub.h GameControllerStub.cc def.h entry.h
	rm -f $(INSTALLDIR)/OPEN-R/MW/OBJS/GAMECTRL.BIN

