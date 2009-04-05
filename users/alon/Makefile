ALCOMMON=$(AL_DIR)/extern/c/aldebaran/alcommon
CXXFLAGS=-I$(ALCOMMON)/include -I$(ALCOMMON)/soap -I$(ALCOMMON)/interface $(shell python2.5-config --cflags)
LDFLAGS=$(shell python2.5-config --ldflags) -L$(AL_DIR)/extern/c/linux/lib -lboost_python -lboost_signals -L$(ALCOMMON)/lib/linux -lalcommon -ltinyxml

all: testvision

testvision: testvision.o
	g++ -o testvision testvision.o $(LDFLAGS)

.PHONY: clean

clean:
	rm *.o testvision

