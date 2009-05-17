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

include ../makefile.config

PREFIX     = /usr/local/OPEN_R_SDK
OPENR_ROOT = $(PREFIX)/OPEN_R

CXX        = $(PREFIX)/bin/mipsel-linux-g++
STRIP      = $(PREFIX)/bin/mipsel-linux-strip
MKBIN      = $(OPENR_ROOT)/bin/mkbin
STUBGEN    = $(OPENR_ROOT)/bin/stubgen2
MKBINFLAGS = -v -p $(PREFIX)
LIBS=-lObjectComm -lOPENR
CP         = rsync -cr

WARNFLAGS = -W -Wcast-qual -Wwrite-strings -Wconversion -Wredundant-decls -Wall

SYSINCLUDES = -isystem$(OPENR_ROOT)/include/R4000 \
			  -isystem$(OPENR_ROOT)/include/MCOOP \
			  -isystem$(OPENR_ROOT)/include

CXXFLAGS = -O2 $(WARNFLAGS) $(SYSINCLUDES)\
		   -g \
		   -DOPENR_DEBUG \
		   -I. \
		   -DAPERIOS

#
# When OPENR_DEBUG is defined, OSYSDEBUG() is available.
#
#CXXFLAGS+= -DOPENR_DEBUG

CC_SRCS = SNDPlay.cc WAV.cc SNDPlayStub.cc

.PHONY: all install clean distclean mkdepend

OBJECT = SNDPlay.bin

all: $(OBJECT)

OBJS = $(patsubst %.cc,%.o,$(filter %.cc,$(CC_SRCS))) $(EXT_OBJS)

%.o: %.cc
	@echo Compiling $<
	@$(CXX) $(CXXFLAGS) -o $@ -c $<

SNDPlayStub.cc: stub.cfg
	$(STUBGEN) stub.cfg	

$(OBJECT): $(OBJS) SNDPlay.ocf
	@echo Linking $@
	@$(MKBIN) $(MKBINFLAGS) -o $@ $^ $(LIBS)
	@echo Stripping $@
	@$(STRIP) $@

install: $(OBJECT).gz
	$(CP) $(OBJECT).gz $(MEMSTICK)/open-r/mw/objs/SNDPLAY.bin

$(OBJECT).gz: $(OBJECT)
	gzip -c $(OBJECT) > $(OBJECT).gz

clean:
	rm -f *.o *.bin *.elf *.snap.cc
	rm -f SNDPlayStub.h SNDPlayStub.cc def.h entry.h
	rm -f $(INSTALLDIR)/OPEN-R/MW/OBJS/SNDPLAY.BIN

depend: SNDPlayStub.cc
	$(CXX) -M $(CXXFLAGS) $(CC_SRCS) > depend

mkdepend:
	rm -f depend
	$(MAKE) depend
	
include depend	
