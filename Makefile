include Makefile.local

all: install

Makefile.local:
	echo Creating a brand new Makefile.local, it contains
	echo the ip of the robot to install to, needs editing
	cp Makefile.local.template Makefile.local
	exit 0

.PHONY: burstmem recordermodule clean

clean:
	rm -R src/burstmem/crossbuild
	rm -R src/recordermodule/crossbuild

burstmem:
	cd src/burstmem; ./makelocal

recordermodule:
	cd src/recordermodule; ./makelocal

install: Makefile.local burstmem recordermodule
	rsync -avr lib root@$(ROBOT):/home/root/burst/

installall: install
	# TODO - each copyto is an ssh initiation, many secundas.
	cd src/burstmem; ./copyto
	cd src/recordermodule; ./copyto

