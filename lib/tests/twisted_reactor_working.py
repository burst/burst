import twisted.internet.reactor as reactor
def f(*args):
 from time import time
 print time()
 reactor.callLater(1.0, f)
f()
reactor.run()
