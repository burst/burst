# Makefile.local is the local configuration,
# contains the ROBOT variable (ip or host name of robot to install to)
include Makefile.local

# We require a TABLE variable defined in Makefile.local
# color table to use, copied to the robot at /home/root/burst/lib/
# from data/tables/
#TABLE=maverick/default.mtb

MODULES=src/imops/build_robot/libimops.so src/burstmem/build_robot/libburstmem.so src/recordermodule/crossbuild/src/librecordermodule.so

all: install

prerequisites:
ifeq ($(TABLE), )
	@echo You must define a table in Makefile.local, i.e. TABLE=maverick/burst_lab.mtb
	@exit 1
else
    echo Using TABLE=$(TABLE)
endif

# Main Targets:
#  robot
#  clean
#  

Makefile.local:
	echo Creating a brand new Makefile.local, it contains
	echo the ip of the robot to install to, needs editing
	cp Makefile.local.template Makefile.local
	exit 0

.PHONY: burstmem recordermodule imops colortable clean webots pynaoqi sizes autoload pyloc pylocatotal cleanpyc removewhitespace todo

cleanpyc:
	@echo "removing pyc files"
	find . -iname "*.pyc" -exec rm \{\} \;

clean: cleanpyc
	cd src/burstmem; $(MAKE) clean
	rm -fR src/recordermodule/crossbuild
	cd src/imops; $(MAKE) clean

removewhitespace:
	find . -iname "*.cpp" -or -iname "*.h" -or -iname "*.py" -exec sed "s/\s\s*$$//" -i \{\} \;

todo:
	git grep TODO | less

sizes:
	ls -l $(MODULES)

pyloc:
	find lib -iname "*.py" | xargs cat | grep -v "^\s*#.*$$" | wc -l
	find . -path ./lib -prune -o -iname "*.py" -print | xargs cat | grep -v "^\s*#.*$$" | wc -l

pyloctotal:
	find . -iname "*.py" | xargs cat | wc -l

webots:
	cd src/imops; $(MAKE) webots

pynaoqi:
	cd src/imops; $(MAKE) pynaoqi

robot: Makefile.local burstmem recordermodule colortable imops

install: prerequisites robot
	rsync -avr --exclude "*.pyc" --exclude ".*.sw?" --exclude imops_pynaoqi*.so --exclude *.kcachegrind lib root@$(ROBOT):/home/root/burst/

installall: install
	# TODO - we use two rsyncs, hence two connections - can this be done better (one ssh session, not two)?
	rsync -v $(MODULES) root@$(ROBOT):/opt/naoqi/modules/lib

# Don't want this in installall - might accidentally erase some module?
autoload:
	scp etc/autoload.ini root@$(ROBOT):/opt/naoqi/modules/lib

# Subtargets

burstmem:
	cd src/burstmem; $(MAKE) cross

recordermodule:
	cd src/recordermodule; ./makelocal

imops:
	cd src/imops; $(MAKE) cross

colortable:
	cp data/tables/$(TABLE) lib/etc/table.mtb
	echo data/tables/$(TABLE) > lib/etc/whichtable.txt

