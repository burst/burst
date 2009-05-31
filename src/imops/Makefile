CFLAGS=-fPIC -ggdb

all: install

install: imops.so
	cp imops.so ../../lib

.PHONY: clean
clean:
	rm imops.so *.o

imops.so: imops.o
	gcc -shared -o imops.so imops.o

