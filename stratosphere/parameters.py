from stratosphere import BaseStratosphereObject
import stratosphere.providers as providers


class Parameter(BaseStratosphereObject):
    RESOURCE = 'resource'
    OUTPUT = 'output'
    PARAMETER = 'parameter'

    props = {
        'Source': (basestring, False),
        'Type': (basestring, False),
        'Variable': (basestring, False),
        'Provider': (providers.LookupProvider, False),
        'Value': (basestring, False)
    }

    valid_types = [RESOURCE, OUTPUT, PARAMETER]

    def __init__(self, title, **kwargs):
        super(Parameter, self).__init__(title, **kwargs)
        self.value = None

    def validate(self, stack):
        # TODO Allow string references to provider; validate it exists
        if self.Source is not None:
            if self.Type not in self.valid_types:
                raise ValueError()
            if self.Variable is None:
                raise ValueError()


class ParameterValueResolver(object):

    def __init__(self, superstack):
        self.superstack = superstack
        self.cfn_provider = providers.CloudFormationLookupProvider()

    def resolve_stack(self, stack):
        for parameter in stack.Parameters:
            self.resolve_parameter(stack, parameter)

    def resolve_parameter(self, stack, parameter):
        if parameter.Value is not None:
            return parameter.Value

        if parameter.Provider is not None:
            return parameter.Provider.lookup(self.superstack, stack)

        self.cfn_provider.lookup(self.superstack, stack, parameter)
