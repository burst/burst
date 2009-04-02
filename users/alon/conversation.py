msgs = [ 
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 430
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:getBrokerInfo></albroker:getBrokerInfo></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 684
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:getBrokerInfoResponse><albroker:return><name>NaoQi</name><architecture>0</architecture><ip>0.0.0.0</ip><port>9559</port><processId>2910</processId><modulePointer>135881488</modulePointer><isABroker>true</isABroker><keepAlive>false</keepAlive></albroker:return></albroker:getBrokerInfoResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 430
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:getBrokerName></albroker:getBrokerName></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 496
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:getBrokerNameResponse><albroker:pBrokerName>NaoQi</albroker:pBrokerName></albroker:getBrokerNameResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 468
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:getInfo><albroker:pModuleName>NaoQi</albroker:pModuleName></albroker:getInfo></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 619
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><al:ALModuleInfo><name>NaoQi</name><architecture>0</architecture><ip>0.0.0.0</ip><port>9559</port><processId>2910</processId><modulePointer>135881488</modulePointer><isABroker>true</isABroker><keepAlive>false</keepAlive></al:ALModuleInfo></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 702
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:registerBroker><albroker:pBrokerToRegister><name>visionmodule</name><architecture>0</architecture><ip>127.0.0.1</ip><port>54010</port><processId>1092</processId><modulePointer>147822472</modulePointer><isABroker>true</isABroker><keepAlive>false</keepAlive></albroker:pBrokerToRegister></albroker:registerBroker></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 484
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:registerBrokerResponse><albroker:unused>0</albroker:unused></albroker:registerBrokerResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 680
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByName><albroker:pModuleName>ALLogger</albroker:pModuleName><albroker:pSearchUp>true</albroker:pSearchUp><albroker:pSearchDown>true</albroker:pSearchDown><albroker:pDontLookIntoBrokerName>visionmodule</albroker:pDontLookIntoBrokerName></albroker:exploreToGetModuleByName></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 709
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByNameResponse><albroker:return><name>ALLogger</name><architecture>0</architecture><ip>192.168.7.108</ip><port>9559</port><processId>2910</processId><modulePointer>-1</modulePointer><isABroker>false</isABroker><keepAlive>false</keepAlive></albroker:return></albroker:exploreToGetModuleByNameResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 680
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByName><albroker:pModuleName>ALLogger</albroker:pModuleName><albroker:pSearchUp>true</albroker:pSearchUp><albroker:pSearchDown>true</albroker:pSearchDown><albroker:pDontLookIntoBrokerName>visionmodule</albroker:pDontLookIntoBrokerName></albroker:exploreToGetModuleByName></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 709
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByNameResponse><albroker:return><name>ALLogger</name><architecture>0</architecture><ip>192.168.7.108</ip><port>9559</port><processId>2910</processId><modulePointer>-1</modulePointer><isABroker>false</isABroker><keepAlive>false</keepAlive></albroker:return></albroker:exploreToGetModuleByNameResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 680
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByName><albroker:pModuleName>ALMemory</albroker:pModuleName><albroker:pSearchUp>true</albroker:pSearchUp><albroker:pSearchDown>true</albroker:pSearchDown><albroker:pDontLookIntoBrokerName>visionmodule</albroker:pDontLookIntoBrokerName></albroker:exploreToGetModuleByName></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 709
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByNameResponse><albroker:return><name>ALMemory</name><architecture>0</architecture><ip>192.168.7.108</ip><port>9559</port><processId>2910</processId><modulePointer>-1</modulePointer><isABroker>false</isABroker><keepAlive>false</keepAlive></albroker:return></albroker:exploreToGetModuleByNameResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 680
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByName><albroker:pModuleName>ALMemory</albroker:pModuleName><albroker:pSearchUp>true</albroker:pSearchUp><albroker:pSearchDown>true</albroker:pSearchDown><albroker:pDontLookIntoBrokerName>visionmodule</albroker:pDontLookIntoBrokerName></albroker:exploreToGetModuleByName></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 709
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByNameResponse><albroker:return><name>ALMemory</name><architecture>0</architecture><ip>192.168.7.108</ip><port>9559</port><processId>2910</processId><modulePointer>-1</modulePointer><isABroker>false</isABroker><keepAlive>false</keepAlive></albroker:return></albroker:exploreToGetModuleByNameResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 678
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByName><albroker:pModuleName>NaoCam</albroker:pModuleName><albroker:pSearchUp>true</albroker:pSearchUp><albroker:pSearchDown>true</albroker:pSearchDown><albroker:pDontLookIntoBrokerName>visionmodule</albroker:pDontLookIntoBrokerName></albroker:exploreToGetModuleByName></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 707
Connection: close

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:exploreToGetModuleByNameResponse><albroker:return><name>NaoCam</name><architecture>0</architecture><ip>192.168.7.108</ip><port>9559</port><processId>2910</processId><modulePointer>-1</modulePointer><isABroker>false</isABroker><keepAlive>false</keepAlive></albroker:return></albroker:exploreToGetModuleByNameResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 701
Connection: keep-alive
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:callNaoqi><albroker:mod>NaoCam</albroker:mod><albroker:meth>register</albroker:meth><albroker:p><item xsi:type="Array"><item xsi:type="xsd:string">testvision_GVM</item><item xsi:type="xsd:int">2</item><item xsi:type="xsd:int">11</item><item xsi:type="xsd:int">15</item></item></albroker:p></albroker:callNaoqi></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 522
Connection: keep-alive

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:callNaoqiResponse><albroker:return><item xsi:type="xsd:string">testvision_GVM</item></albroker:return></albroker:callNaoqiResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 606
Connection: keep-alive
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:callNaoqi><albroker:mod>NaoCam</albroker:mod><albroker:meth>getImageRemote</albroker:meth><albroker:p><item xsi:type="Array"><item xsi:type="xsd:string">testvision_GVM</item></item></albroker:p></albroker:callNaoqi></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 1246627
Connection: keep-alive

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:callNaoqiResponse><albroker:return><item xsi:type="Array"><item xsi:type="xsd:int">640</item><item xsi:type="xsd:int">480</item><item xsi:type="xsd:int">3</item><item xsi:type="xsd:int">11</item><item xsi:type="xsd:int">1238837866</item><item xsi:type="xsd:int">200370</item><item xsi:type="xsd:base64Binary">kJ2Qj5yPkpySkpySk5yVk5yVk5yVkpuUk5qWk5qWj5mSkJqTkJyPkp2QkJ+MkaCNlKKMlKKM
lqCLl6GMmaCMmqKNl6GMl6GMkp6Jkp6JkJ6JlaONlKCQlaGRl6CTl6CTlp+Slp+SlJ+SlJ+S
j52Nj52NlKGOlKGOlaGRlaGRlqCQlqCQl56SmKCTl56SmKCTmqGPmqGPm6OPmqKNmKGPl6CO
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
</item></item></albroker:return></albroker:callNaoqiResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 604
Connection: keep-alive
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:callNaoqi><albroker:mod>NaoCam</albroker:mod><albroker:meth>releaseImage</albroker:meth><albroker:p><item xsi:type="Array"><item xsi:type="xsd:string">testvision_GVM</item></item></albroker:p></albroker:callNaoqi></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 506
Connection: keep-alive

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:callNaoqiResponse><albroker:return><item xsi:type="xsd:int">1</item></albroker:return></albroker:callNaoqiResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
,
"""
POST / HTTP/1.1
Host: nao.local:9559
User-Agent: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 602
Connection: keep-alive
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:callNaoqi><albroker:mod>NaoCam</albroker:mod><albroker:meth>unRegister</albroker:meth><albroker:p><item xsi:type="Array"><item xsi:type="xsd:string">testvision_GVM</item></item></albroker:p></albroker:callNaoqi></SOAP-ENV:Body></SOAP-ENV:Envelope>HTTP/1.1 200 OK
Server: gSOAP/2.7
Content-Type: text/xml; charset=utf-8
Content-Length: 473
Connection: keep-alive

<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"><SOAP-ENV:Body><albroker:callNaoqiResponse><albroker:return></albroker:return></albroker:callNaoqiResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>
"""
]

