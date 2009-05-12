include Makefile.local

all: install

Makefile.local:
	echo Creating a brand new Makefile.local, it contains
	echo the ip of the robot to install to, needs editing
	cp Makefile.local.template Makefile.local
	exit 0

install: Makefile.local
	rsync -avr lib root@$(ROBOT):/home/root/burst/

