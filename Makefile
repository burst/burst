# Makefile.local is the local configuration,
# contains the ROBOT variable (ip or host name of robot to install to)
include Makefile.local

# color table to use, copied to the robot at /home/root/burst/lib/
# from data/tables/
TABLE=maverick/default.mtb

all: install

# Main Targets:
#  robot
#  clean
#  

Makefile.local:
	echo Creating a brand new Makefile.local, it contains
	echo the ip of the robot to install to, needs editing
	cp Makefile.local.template Makefile.local
	exit 0

.PHONY: burstmem recordermodule imops colortable clean webots pynaoqi

clean:
	rm -R src/burstmem/crossbuild
	rm -R src/recordermodule/crossbuild
	cd src/imops; $(MAKE) clean

webots:
	cd src/imops; $(MAKE) webots

pynaoqi:
	cd src/imops; $(MAKE) pynaoqi

install: Makefile.local burstmem recordermodule colortable
	rsync -avr --exclude "*.pyc" --exclude ".*.sw?" --exclude imops_pynaoqi*.so --exclude *.kcachegrind lib root@$(ROBOT):/home/root/burst/

installall: install imops
	# TODO - each copyto is an ssh initiation, many secundas.
	cd src/burstmem; ./copyto
	cd src/recordermodule; ./copyto

# Subtargets

burstmem:
	cd src/burstmem; ./makelocal

recordermodule:
	cd src/recordermodule; ./makelocal

imops:
	cd src/imops; $(MAKE) cross

colortable:
	cp data/tables/$(TABLE) lib/etc/table.mtb
	echo data/tables/$(TABLE) > lib/etc/whichtable.txt

