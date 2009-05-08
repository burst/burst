IP=192.168.7.109
#IP=192.168.7.X:
# gerrard - 107 maldini - 110 raul - 109
install:
	rsync -avr lib root@$(IP):/home/root/burst/
