from stratosphere import BaseStratosphereObject, Stack
import stratosphere.providers as providers


class Parameter(BaseStratosphereObject):
    props = {
        'Source': ((Stack, basestring), False),
        'Type': (basestring, False),
        'Variable': (basestring, False),
        'Provider': (providers.LookupProvider, False),
        'Value': (basestring, False)
    }

    RESOURCE = 'resource'
    OUTPUT = 'output'
    PARAMETER = 'parameter'
    valid_types = [RESOURCE, OUTPUT, PARAMETER]

    def __init__(self, title, **kwargs):
        super(Parameter, self).__init__(title, **kwargs)

    def validate(self, stack):
        # TODO Allow string references to provider; validate it exists
        if self.Source is not None:
            if not isinstance(self.Source, Stack):
                raise TypeError('source must be of type stratosphere.Stack')
            if self.Type not in self.valid_types:
                raise ValueError(
                    'type must be one of "resource", "output" or "parameter", '
                    '"%s" given' % (self.Type,)
                )
            if self.Variable is None:
                raise ValueError('variable must not be blank')
        elif self.Provider is None and self.Value is None:
            raise ValueError('a parameter must have either a value, provider '
                             'or stack resource reference')


class ParameterValueResolver(object):

    def __init__(self, superstack, cfn_provider):
        self.superstack = superstack
        self.cfn_provider = cfn_provider

    def resolve_stack(self, stack):
        for parameter in stack.Parameters:
            self.resolve_parameter(stack, parameter)

    def resolve_parameter(self, stack, parameter):
        if parameter.Value is not None:
            return parameter.Value

        if parameter.Provider is not None:
            return parameter.Provider.lookup(self.superstack, stack)

        self.cfn_provider.lookup(self.superstack, stack, parameter)
