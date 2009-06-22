from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.primitive import String, Integer, Array

class HelloWorldService(SimpleWSGISoapApp):

    @soapmethod(String,Integer,_returns=Array(String))
    def say_hello(self,name,times):
        results = []
        for i in range(0,times):
            results.append('Hello, %s'%name)
        return results

def main():
    from soaplib.client import make_service_client
    client = make_service_client('http://localhost:9999/', HelloWorldService())
    print client.say_hello("Dave",5)

if __name__=='__main__':
    main()

