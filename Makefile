IP=192.168.7.110

install:
	rsync -avr lib root@$(IP):/home/root/burst/
