import unittest
from stratosphere import Stack
from stratosphere.parameters import Parameter


class TestParameter(unittest.TestCase):

    def test_value(self):
        param = Parameter(
            'Foo',
            Value='bar'
        )
        self.assertEqual(param.Value, 'bar')

    def test_badsource(self):
        with self.assertRaises(TypeError):
            param = Parameter(
                'Foo',
                Source='nope'
            )
            param.validate(None)

    def test_badsourcetype(self):
        with self.assertRaises(ValueError):
            param = Parameter(
                'Foo',
                Source=Stack('Bar'),
                Type='nope'
            )
            param.validate(None)

class TestParameterValueResolver(unittest.TestCase):
    pass
