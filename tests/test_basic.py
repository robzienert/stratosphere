import unittest
from stratosphere import Superstack, Stack, BaseStratosphereObject


class TestBasic(unittest.TestCase):

    def test_badproperty(self):
        with self.assertRaises(AttributeError):
            Stack('MyStack', foobar=True,)

    def test_badrequired(self):
        with self.assertRaises(ValueError):
            s = Stack('MyStack')
            s.validate(Superstack('SomeSuperstack'))

    def test_badtype(self):
        with self.assertRaises(TypeError):
            Stack('MyStack', Description=1.1)

    def test_goodrequired(self):
        Stack('MyStack', CloudFormationTemplate='foo.json')

    def test_goodproperty(self):
        stack = Stack('MyStack', CloudFormationTemplate='foo.json')
        self.assertEqual(stack.CloudFormationTemplate, 'foo.json')

    def test_extraattribute(self):
        class ExtendedStack(Stack):
            def __init__(self, *args, **kwargs):
                self.attribute = None
                super(ExtendedStack, self).__init__(*args, **kwargs)

        stack = ExtendedStack('MyStack', attribute='value')
        self.assertEqual(stack.attribute, 'value')


def call_correct(x):
    return x


def call_incorrect(x):
    raise ValueError


class FakeStratosphereObject(BaseStratosphereObject):
    props = {
        'callcorrect': (call_correct, False),
        'callincorrect': (call_incorrect, False),
        'singlelist': (list, False),
        'multilist': ([bool, int, float], False),
        'multituple': ((bool, int), False),
    }

    def validate(self, superstack):
        properties = self.properties
        title = self.title
        if 'callcorrect' in properties and 'singlelist' in properties:
            raise ValueError(
                'cannot specify both "callcorrect" and "singlelist" in '
                'object %s' % (title,)
            )


class TestValidators(unittest.TestCase):
    def test_callcorrect(self):
        FakeStratosphereObject('fake', callcorrect=True)

    def test_callincorrect(self):
        with self.assertRaises(AttributeError):
            FakeStratosphereObject('fake', call_incorrect=True)

    def test_list(self):
        FakeStratosphereObject('fake', singlelist=['a', 1])

    def test_badlist(self):
        with self.assertRaises(TypeError):
            FakeStratosphereObject('fake', singlelist=True)

    def test_multilist(self):
        FakeStratosphereObject('fake', multilist=[1, True, 2, 0.3])

    def test_badmultilist(self):
        with self.assertRaises(TypeError):
            FakeStratosphereObject('fake', multilist=True)
        with self.assertRaises(TypeError):
            FakeStratosphereObject('fake', multilist=[1, 'a'])

    def test_mutualexclusion(self):
        fake = FakeStratosphereObject(
            'fake', callcorrect=True, singlelist=[10]
        )
        with self.assertRaises(ValueError):
            fake.validate(None)

    def test_tuples(self):
        FakeStratosphereObject('fake', multituple=True)
        FakeStratosphereObject('fake', multituple=10)
        with self.assertRaises(TypeError):
            FakeStratosphereObject('fake', multituple=0.1)
