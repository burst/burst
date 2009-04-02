class XMLObject(object):
    def __init__(self, name, attrs=[], children=[]):
        self._name = name
        self._attrs = attrs
        self._children = children
    def attributes(self, attrs):
        self._attrs = attrs
        return self
    As = attributes
    def attr(self, k, v):
        self._attrs.append((k, v))
        return self
    A = attr
    def child(self, c):
        self._children.append(c)
        return self
    C = child
    def __str__(self):
        spacer = self._attrs and ' ' or ''
        return '<%s%s%s>%s</%s>' % (self._name, spacer, ' '.join('%s="%s"' % (k, v) for k, v in self._attrs), '\n'.join(str(c) for c in self._children), self._name)

def test():
    X = XMLObject
    print X('SOAP-ENV:Envelope')
    attrs = [(lambda (a,b): (a, b[1:-1]))(n.split('=')) for n in 'xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"'.split(' ')]
    print X('SOAP-ENV:Envelope', attrs=attrs)
    print X('SOAP-ENV:Envelope', attrs,
            [
                X('SOAP-ENV:Body', [],
                    [
                        X('albroker:getInfo', [],
                            [
                                X('albroker:pModuleName', [], ['NaoQi'])
                            ])
                    ])
            ])

if __name__ == '__main__':
    test()

