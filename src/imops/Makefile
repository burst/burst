CFLAGS=-fPIC

all: install

install: imops.so
	cp imops.so ../../lib

imops.so: imops.o
	gcc -shared -o imops.so imops.o

