import burst

class AlonModule(burst.ALModule):
    def sayhello(self):
        print "hello"

burst.init()

alonModule = AlonModule("AlonModule")
alonModule.BIND_PYTHON("alonModule", "sayhello")

