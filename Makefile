IP=192.168.7.107
#IP=192.168.7.X:
# gerrard - 107 maldini - 110
install:
	rsync -avr lib root@$(IP):/home/root/burst/
